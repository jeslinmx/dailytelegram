import os
from textwrap import dedent

envs = {
    "api_token": os.getenv("TELEGRAM_API_TOKEN"),
    "devs": os.getenv("LOG_RECIPIENTS", "").split(","),
    "asap_freq": int(os.getenv("ASAP_UPDATE_FREQ", 5)),
    "pkl_location": os.getenv("BOT_DATA", ".")
}


strings = {
    "welcome": dedent("""\
        Welcome to <i>The Daily Telegram</i>!
        You may want to /add some feeds, or get /help on how to use this bot.
    """),
    "alreadyinitialized": dedent("""\
        You are already using <i>The Daily Telegram</i>.

        Updates from your feeds will automatically be sent to you as they are published, or in a daily summary, depending on per-feed settings.

        If you haven't already, you may want to /add feeds, or get /help on how to use this bot.
    """),
    "uninitialized": dedent("""\
        I'm afraid I can't do anything unless you /start me first.
    """),
    "help": dedent("""\
        Welcome to <i>The Daily Telegram</i>, an RSS notifier bot!

        You may /add feeds in one of 2 lists:
        - <b>ASAP</b> feeds will have updates sent to you as soon as they are published.
        - <b>Daily Digest</b> feeds will have their updates aggregated into a daily summary, sent at a /setdigesttime.

        You can view your feeds in /settings, /remove feeds, and for advanced users, /edit how they are presented.

        Wish to zone out from your updates for a bit? You can use Telegram's disable notifications function, and archive this conversation to hide it from your chats. I don't mind.
    """),
    "unknowninput": dedent("""\
        Sorry, that input was not recognized. Do you need /help?
    """),
    "showfeeds": dedent("""\
        <b>ASAP feeds:</b>
        <i>(updates arrive as soon as they are posted)</i>
        {asap}
        
        <b>Daily Digest</b>
        <i>(a summary will arrive on a daily basis)</i>
        {digest}

        <i>Feeds marked with a + have a custom presentation.</i>
    """),
    "nofeeds": dedent("""\
        You currently have no feeds. You may want to /add some feeds, or get /help on how to use this bot.
    """),
    "add_success": dedent("""\
        Successfully subscribed to {urls}
    """),
    "add_dupurl": dedent("""\
        You are already subscribed to {urls}.
    """),
    "add_requesturl": dedent("""\
        Please enter the feed URL.
        <i>(or /cancel feed adding)</i>
    """),
    "add_requestmode": dedent("""\
        Do you wish to receive updates from this feed ASAP or in a daily digest?
        <i>(or /cancel feed adding)</i>
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
        <i>(or /cancel feed removal)</i>
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
        <a href='{entry[title]}'>{entry[link]}</a> - {feed[title]}
    """),
    "digestheader": dedent("""\
        <b>Daily digest from <a href='{feed[title]}'>{feed[link]}</a></b>
        ---
    """),
    "digestdefaultrepr": dedent("""\
        - <a href='{entry[title]}'>{entry[link]}</a>
    """),
    "reprerror": dedent("""\
        <pre>the repr for {url} is invalid and could not be processed.</pre>
    """),
    "fperror": dedent("""\
         An error occurred while parsing the feed {url}. The devs have been notified; notifications from this feed have been put on pause for 24 hours while we see what can be done.
    """),
    "fperrorreport": dedent("""\
         Error encountered while parsing {url}. Traceback:
         <pre>{trace}</pre>
    """),
    "error": dedent("""\
        An unforeseen error occurred in the bot. The devs have been notified.
    """),
    "errorreport": dedent("""\
        Error encountered in {chat}. Traceback:
        <pre>{trace}</pre>
    """),
}