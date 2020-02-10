# The Daily Telegram

A simple Telegram RSS bot which notifies of updates in one of 2 per-feed modes:

- `asap` - Each new post is sent to the user as soon as the feed is updated (or at least, as soon as the bot polls it)
- `digest` - The bot polls the feed on a daily basis, and sends a summary of the day's new posts

## Usage

The prompts provided by the bot should be self-explanatory. Nevertheless, a listing of the commands supported are provided below:

- `/start` - Start receiving from the Daily Telegram
- `/add <url> <mode>` - Subscribe to a feed
- `/remove <url>` - Unsubscribe from a feed
- `/edit <url> <repr>` - Change advanced settings for a feed
- `/cancel` - Cancel the current operation
- `/settings` - Show subscribed feeds
- `/help` - Get help on how to use this bot

## Development

This bot is in a very early (but mostly workable) state. Pull requests are welcome!

The following environment variables are used by the bot:

- `TELEGRAM_API_TOKEN` - token for the Telegram Bot API
- `LOG_RECIPIENTS` (optional) - comma-separated list of Telegram chat IDs to which tracebacks will be sent
- `ASAP_UPDATE_FREQ` (optional) - update interval (in seconds) for feeds in `asap` mode (defaults to 5 minutes)
- `BOT_DATA` (optional) - directory from which pickle files will be read from/written to to persist user settings across bot restarts

The prompts may be customized or translated to a new language in the `strings` dict in `localconfig.py`.
