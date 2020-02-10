import os
from textwrap import dedent

envs = {
    "api_token": os.getenv("TELEGRAM_API_TOKEN"),
    "devs": os.getenv("LOG_RECIPIENTS", "").split(","),
    "asap_freq": int(os.getenv("ASAP_UPDATE_FREQ", 5 * 60)),
    "pkl_location": os.getenv("BOT_DATA", ".")
}


strings = {
    "welcome": dedent("""\
        Welcome to _The Daily Telegram_!
        You may want to /add some feeds, or get /help on how to use this bot.
    """),
    "alreadyinitialized": dedent("""\
        You are already using _The Daily Telegram_.

        Updates from your feeds will automatically be sent to you as they are published, or in a daily summary, depending on per-feed settings.

        If you haven't already, you may want to /add feeds, or get /help on how to use this bot.
    """),
    "uninitialized": dedent("""\
        I'm afraid I can't do anything unless you /start me first.
    """),
    "help": dedent("""\
        Welcome to _The Daily Telegram_, an RSS notifier bot!

        You may /add feeds in one of 2 lists:
        - *ASAP* feeds will have updates sent to you as soon as they are published.
        - *Daily Digest* feeds will have their updates aggregated into a daily summary, sent at a /setdigesttime.

        You can view your feeds in /settings, /remove feeds, and for advanced users, /edit how they are presented.

        Wish to zone out from your updates for a bit? You can use Telegram's disable notifications function, and archive this conversation to hide it from your chats. I don't mind.
    """),
    "unknowninput": dedent("""\
        Sorry, that input was not recognized. Do you need /help?
    """),
    "showfeeds": dedent("""\
        *ASAP feeds:*
        _(updates arrive as soon as they are posted)_
        {asap}
        
        *Daily Digest*
        _(a summary will arrive on a daily basis)_
        {digest}

        _Feeds marked with a + have a custom presentation._
    """),
    "nofeeds": dedent("""\
        You currently have no feeds. You may want to /add some feeds, or get /help on how to use this bot.
    """),
    "add_success": dedent("""\
        Feed added successfully.
    """),
    "add_dupurl": dedent("""\
        You are already subscribed to this feed.
    """),
    "add_requesturl": dedent("""\
        Please enter the feed URL.
        _(or /cancel feed adding)_
    """),
    "add_requestmode": dedent("""\
        Do you wish to receive updates from this feed ASAP or in a daily digest?
        _(or /cancel feed adding)_
    """),
    "add_cancel": dedent("""\
        Feed adding cancelled.
    """),
    "add_urlwhat": dedent("""\
        Sorry, I did not understand that input. Please enter a single feed URL.
    """),
    "add_modewhat": dedent("""\
        Sorry, I did not understand that input. Please enter either "digest" or "asap".
    """),
    "remove_requesturl": dedent("""\
        Please enter the feed URL to remove.
        _(or /cancel feed removal)_
    """),
    "remove_success": dedent("""\
        Feed {url} removed successfully.
    """),
    "remove_feednotfound": dedent("""\
        Feed {url} was not found in your feeds.
    """),
    "remove_what": dedent("""\
        Sorry, I did not understand that input. Please enter a valid feed URL.
    """),
    "remove_cancel": dedent("""\
        Feed deletion cancelled.
    """),
    "asapdefaultrepr": dedent("""\
        [{entry[title]}]({entry[link]}) - {feed[title]}
    """),
    "digestheader": dedent("""\
        *Daily digest from [{feed[title]}]({feed[link]})*
        ---
    """),
    "digestdefaultrepr": dedent("""\
        - ({entry[published]}) [{entry[title]}]({entry[link]})
    """),
    "reprerror": dedent("""\
        `the repr for {url} is invalid and could not be processed.`
    """),
    "error": dedent("""\
        An unforseen error occurred. The devs have been notified.
    """),
    "errorreport": dedent("""\
    `{errorType}: {error}` occurred. Traceback:

    ```{trace}```
    """),
}