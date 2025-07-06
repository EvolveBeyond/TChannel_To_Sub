from aiogram import Router, types
from aiogram.filters import CommandStart # More specific import for /start
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton # Not used in this version

router = Router() # Create a router instance for these handlers

@router.message(CommandStart()) # Use CommandStart filter
async def start_handler(msg: types.Message):
    text = (
        "👋 Welcome! This bot manages your Telegram channel subscriptions.\n\n"
        "I will periodically fetch new subscription links from the Telegram channels you specify, "
        "categorize them, and push them to your configured GitHub repository.\n\n"
        "**Available Commands:**\n"
        "  `/start` - Show this welcome message and command list.\n"
        "  `/tch @ChannelUsername` or `/tch https://t.me/channelusername` - Add or remove a Telegram channel for monitoring. Using the channel's username (e.g., `@mychannel`) or its public link is recommended.\n"
        "  `/status` - Show information about the last subscription update status (via GitHub Actions).\n\n"
        "**How to get started:**\n"
        "1. Make sure you have forked this bot's repository and configured the necessary GitHub Secrets (`BOT_TOKEN`, `GITHUB_TOKEN`, `DEFAULT_REPO`) as per the README.\n"
        "2. Use the `/tch` command to add the Telegram channels you want to get subscription links from.\n\n"
        "The bot will then automatically update your subscription files in the GitHub repository specified in `DEFAULT_REPO`."
    )
    # Using MarkdownV2 for formatting. Ensure bot is initialized with parse_mode='MarkdownV2' or use it here.
    # For simplicity, let's stick to plain text or simple Markdown if parse_mode isn't globally set.
    # The original text was plain. Let's improve it slightly with Markdown.
    # To use Markdown, specify parse_mode.
    await msg.answer(text, parse_mode="Markdown")
