import datetime
import logging
import random
import traceback
from collections import defaultdict

from telegram import (
    MessageEntity,
    ParseMode,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    PicklePersistence,
    Updater,
)
from telegram.ext.dispatcher import run_async

from fpwrapper import FeedCollection, FeedCollectionError
from localconfig import strings, envs

# declare symbols for conversation states
MAIN, ADD_URL, ADD_MODE, REMOVE_URL, EDIT_URL, EDIT_REPR = map(chr, range(6))

class SimpleReplies(object):
    """Wrapper providing simple functions which reply with no side effects"""
    def __getitem__(self, key):
        @run_async
        def r(upd: Update, ctx: CallbackContext, mapping: dict = {}, **kwargs):
            upd.message.reply_text(
                text=strings[key].format_map(mapping),
                parse_mode=ParseMode.MARKDOWN,
                **kwargs
            )
        return r
reply = SimpleReplies()

# simple command callbacks
def start(upd: Update, ctx: CallbackContext):
    """Initializes user settings and moves main_conv into MAIN"""
    ctx.chat_data["feeds"] = {
        "asap": FeedCollection([]),
        "digest": FeedCollection([]),
    }
    ctx.chat_data["reprs"] = {}
    ctx.chat_data["digesttime"] = datetime.time(0, 0, 0)
    # enroll user in job_queue
    ctx.job_queue.run_repeating(
        callback=asap_update,
        interval=envs["asap_freq"],
        first=random.randrange(0, envs["asap_freq"]), # random staggering
        context=upd.effective_chat.id,
    )
    ctx.job_queue.run_daily(
        callback=digest_update,
        time=ctx.chat_data["digesttime"],
        context=upd.effective_chat.id,
    )

    reply["welcome"](upd, ctx)
    return MAIN

def show_feeds(upd: Update, ctx: CallbackContext):
    """Pretty prints user feeds"""
    feeds = {
        mode : "\n".join((
            f"{'+' if feed_url in ctx.chat_data['reprs'] else '-'} [{feed.metadata['title']}]({feed_url})"
            for feed_url, feed
            in ctx.chat_data["feeds"][mode].feeds.items()
        ))
        for mode in ("asap", "digest")
    }
    if not feeds["asap"] and not feeds["digest"]:
        reply["nofeeds"](upd, ctx)
    else:
        reply["showfeeds"](upd, ctx, mapping=feeds, disable_web_page_preview=True)

# add flow callbacks
def add_command(upd: Update, ctx: CallbackContext):
    """Processes args of /add and hands over to add_feed"""
    # look for urls
    if upd.message.parse_entities(types=[MessageEntity.URL]).values():
        ctx.chat_data["add_url"] = list(upd.message.parse_entities(types=[MessageEntity.URL]).values())

    # look for mode in last argument
    if len(ctx.args) >= 1 and ctx.args[-1].lower() in ("digest", "asap"):
        ctx.chat_data["add_mode"] = ctx.args[-1].lower()
    
    return add_feed(upd, ctx)

def add_url_step(upd: Update, ctx: CallbackContext):
    """Processes feed URL and hands over to add_feed"""
    if upd.message.parse_entities(types=[MessageEntity.URL]).values():
        ctx.chat_data["add_url"] = list(upd.message.parse_entities(types=[MessageEntity.URL]).values())
        return add_feed(upd, ctx)
    else:
        return reply["add_urlwhat"](upd, ctx)

def add_mode_step(upd: Update, ctx: CallbackContext):
    """Processes feed mode and hands over to add_feed"""
    ctx.chat_data["add_mode"] = upd.message.text.lower()
    return add_feed(upd, ctx)

def add_cancel_conversation(upd: Update, ctx: CallbackContext):
    """Resets keyboard and moves main_conv back to MAIN"""
    reply["add_cancel"](upd, ctx,
        reply_markup=ReplyKeyboardRemove(selective=True)
    )
    return add_cleanup(upd, ctx)

def add_feed(upd: Update, ctx: CallbackContext):
    """Checks ctx for args and adds feed/directs to correct state"""
    if "add_url" not in ctx.chat_data:
        # direct user to send url
        reply["add_requesturl"](upd, ctx)
        return ADD_URL
    elif "add_mode" not in ctx.chat_data:
        # direct user to input mode
        reply["add_requestmode"](upd, ctx,
            reply_markup=ReplyKeyboardMarkup(
                [["ASAP", "Digest"]],
                resize_keyboard=True,
                selective=True
            )
        )
        return ADD_MODE
    else:
        # proceed to add feeds
        success = []
        duplicates = []
        for url in ctx.chat_data["add_url"]:
            try:
                ctx.chat_data["feeds"][ctx.chat_data["add_mode"]].add_feed(url)
            except FeedCollectionError:
                duplicates.append(url)
            else:
                success.append(url)
        if success:
            reply["add_success"](upd, ctx,
                mapping={"urls":", ".join(success)},
                reply_markup=ReplyKeyboardRemove(selective=True),
                disable_web_page_preview=True,
            )
        if duplicates:
            reply["add_dupurl"](upd, ctx,
                mapping={"urls":", ".join(duplicates)},
                reply_markup=ReplyKeyboardRemove(selective=True),
                disable_web_page_preview=True,
            )
        return add_cleanup(upd, ctx)

def add_cleanup(upd: Update, ctx: CallbackContext):
    """Clears out add context before returning to MAIN"""
    try:
        del ctx.chat_data["add_url"]
        del ctx.chat_data["add_mode"]
    except KeyError:
        pass
    return MAIN

# remove flow callbacks
def remove_command(upd: Update, ctx: CallbackContext):
    """Grabs URLs from entities and removes feeds, or bumps to REMOVE_URL if not found"""
    urls = upd.message.parse_entities(types=[MessageEntity.URL]).values()
    if len(urls) < 1:
        reply["remove_requesturl"](upd, ctx,
            reply_markup=ReplyKeyboardMarkup(
                [
                    [url] for url in {
                        feed
                        for mode, fc in ctx.chat_data["feeds"].items()
                        for feed in fc.feeds
                    }
                ],
                resize_keyboard=True,
                selective=True,
            )
        )
        return REMOVE_URL
    # remove feeds from either FeedCollection
    for url in urls:
        _exc_counter = 0
        try:
            ctx.chat_data["feeds"]["asap"].remove_feed(url)
        except FeedCollectionError:
            _exc_counter += 1
        try:
            ctx.chat_data["feeds"]["digest"].remove_feed(url)
        except FeedCollectionError:
            _exc_counter += 1
        if _exc_counter >= 2:
            reply["remove_feednotfound"](upd, ctx,
                mapping={"url": url},
                reply_markup=ReplyKeyboardRemove(selective=True),
                disable_web_page_preview=True,
            )
        else:
            reply["remove_success"](upd, ctx,
                mapping={"url": url},
                reply_markup=ReplyKeyboardRemove(selective=True),
                disable_web_page_preview=True,
            )
    return MAIN

def remove_cancel_conversation(upd: Update, ctx: CallbackContext):
    reply["remove_cancel"](upd, ctx,
        reply_markup=ReplyKeyboardRemove(selective=True),
        disable_web_page_preview=True,
    )
    return MAIN

# job_queue callbacks
def format_feeds(ctx: CallbackContext, fc: FeedCollection, reprs: dict, defaultrepr: str):
    """Gets new entries from a FeedCollection and formats them according to reprs/defaultrepr"""
    entries = fc.get_new_entries()
    formatted = {}
    for url in entries:
        try:
            formatted[url] = [
                (
                    reprs[url] if url in reprs
                    else defaultrepr
                ).format(
                    entry=entry,
                    feed=fc.feeds[url].metadata,
                ) for entry in entries[url]
            ]
        except TypeError:
            # return a simple string representation
            # this shoud only occur if an Exception was raised
            # from parsing this feed, resulting in a exc_info tuple
            formatted[url] = [strings["fperror"].format(
                url=url,
            )]
            report(ctx, strings["fperrorreport"],
                url=url,
                trace="".join(traceback.format_exception(*entries[url])),
            )
        except KeyError:
            formatted[url] = [strings["reprerror"].format(url=url)]
        # remove feed from result if it is empty
        if not formatted[url]:
            del formatted[url]
    return formatted

@run_async
def asap_update(ctx: CallbackContext):
    chat_id = ctx.job.context
    fc = ctx.dispatcher.chat_data[chat_id]["feeds"]["asap"]
    reprs = ctx.dispatcher.chat_data[chat_id]["reprs"]
    formatted = format_feeds(ctx, fc, reprs, strings["asapdefaultrepr"])
    for url in formatted:
        for entry in reversed(formatted[url]):
            ctx.bot.send_message(
                chat_id=chat_id,
                text=entry,
                parse_mode=ParseMode.MARKDOWN,
            )

@run_async
def digest_update(ctx: CallbackContext):
    chat_id = ctx.job.context
    fc = ctx.dispatcher.chat_data[chat_id]["feeds"]["digest"]
    reprs = ctx.dispatcher.chat_data[chat_id]["reprs"]
    formatted = format_feeds(ctx, fc, reprs, strings["digestdefaultrepr"])
    for url in formatted:
        msgheader = strings["digestheader"].format(
            feed=fc.feeds[url].metadata,
        )
        msgbody = "\n".join(reversed(formatted[url]))
        ctx.bot.send_message(
            chat_id=chat_id,
            text="\n".join([msgheader, msgbody]),
            parse_mode=ParseMode.MARKDOWN
        )

# error handlers
def bot_error(upd: Update, ctx: CallbackContext):
    # notify user
    if upd.effective_message:
        upd.effective_message.reply_text(strings["error"])

    # report to devs
    report(ctx, strings["errorreport"],
        chat = (
            upd.effective_user.mention_markdown() if upd.effective_user
            else f"@{upd.effective_chat.username}" if upd.effective_chat
            else "???"
        ),
        trace=traceback.format_exc(),
    )
    
    # Re-raise the exception for the sake of the logger.
    raise

def report(ctx: CallbackContext, template: str, **kwargs):
    for dev_id in envs["devs"]:
        ctx.bot.send_message(
            chat_id=dev_id,
            parse_mode=ParseMode.MARKDOWN,
            text=template.format(**kwargs),
        )


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    updater = Updater(
        token=envs["api_token"],
        use_context=True,
        persistence=PicklePersistence(filename=f"{envs['pkl_location']}/bot.pkl")
    )

    dispatcher = updater.dispatcher
    dispatcher.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            MAIN: [
                CommandHandler("settings", show_feeds),
                CommandHandler("help", reply["help"]),
                CommandHandler("start", reply["alreadyinitialized"]),
                CommandHandler("add", add_command),
                CommandHandler("remove", remove_command),
                # CommandHandler("edit", edit_command),
            ],
            ADD_URL: [
                MessageHandler(Filters.entity(MessageEntity.URL), add_url_step),
                CommandHandler("cancel", add_cancel_conversation),
                MessageHandler(Filters.all, reply["add_urlwhat"]),
            ],
            ADD_MODE: [
                MessageHandler(Filters.regex(r"^(?i:digest)|(?i:asap)$"), add_mode_step),
                CommandHandler("cancel", add_cancel_conversation),
                MessageHandler(Filters.all, reply["add_modewhat"]),
            ],
            REMOVE_URL: [
                MessageHandler(Filters.entity(MessageEntity.URL), remove_command),
                CommandHandler("cancel", remove_cancel_conversation),
                MessageHandler(Filters.all, reply["remove_what"]),
            ],
            # EDIT_URL: [],
            # EDIT_REPR: [],
        },
        fallbacks=[
            MessageHandler(Filters.all, reply["unknowninput"]),
        ],
        persistent=True,
        name="main_conv"
    ))
    dispatcher.add_handler(MessageHandler(Filters.all, reply["uninitialized"]))
    dispatcher.add_error_handler(bot_error)

    job_queue = dispatcher.job_queue
    # enqueue update jobs for persisted users
    for chat_id in dispatcher.chat_data:
        # check if chat_data is actually populated by data from /start
        if dispatcher.chat_data[chat_id]:
            job_queue.run_repeating(
                callback=asap_update,
                interval=envs["asap_freq"],
                first=random.randrange(0, envs["asap_freq"]), # random staggering
                context=chat_id,
            )
            job_queue.run_daily(
                callback=digest_update,
                time=dispatcher.chat_data[chat_id]["digesttime"],
                context=chat_id,
            )

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()