import asyncio
from aiogram import Bot
import re
import logging

# Configure basic logging if not already configured elsewhere
# logging.basicConfig(level=logging.INFO) # Potentially configure in main bot.py

async def fetch_channel_posts(bot: Bot, channel: str | int, limit: int = 50) -> list[str]:
    """
    Fetches the text content of the last 'limit' messages from a given channel.
    Includes both message text and captions.
    Compatible with Aiogram 3.x.
    """
    posts_texts: list[str] = []
    try:
        logging.info(f"Fetching last {limit} messages from channel '{channel}'.")
        # In Aiogram 3.x, get_chat_history returns List[Message]
        messages = await bot.get_chat_history(chat_id=channel, limit=limit)

        for msg in messages:
            if msg.text:
                posts_texts.append(msg.text)
            elif msg.caption: # Also consider message captions for links
                posts_texts.append(msg.caption)
        logging.info(f"Fetched {len(posts_texts)} text/caption entries from {len(messages)} messages in channel '{channel}'.")

    # Specific exceptions can be caught from aiogram.exceptions if needed
    # Example: ChatNotFound, BotBlocked, etc.
    # For now, a general catch for robustness.
    except Exception as e:
        logging.error(f"Error fetching posts from channel '{channel}': {type(e).__name__} - {e}")
        return [] # Return empty list on error
    return posts_texts

def extract_links(text: str) -> list[str]:
    """
    Extracts all unique URI links from a given text.
    Uses a regex that is generally good for common URLs and then cleans trailing punctuation.
    """
    # This regex captures a scheme, '://', and then any non-whitespace/quote/angle-bracket characters.
    # It's a good general pattern that includes most valid URL characters.
    # Scheme: [a-zA-Z][a-zA-Z0-9+.-]* (e.g., http, https, ftp, custom_scheme)
    # Path/Host etc.: [^\s\"'<>]+ (anything not whitespace, quotes, or angle brackets)
    url_pattern = re.compile(r"([a-zA-Z][a-zA-Z0-9+.-]*:\/\/[^\s\"'<>]+)")

    matches = url_pattern.findall(text)

    cleaned_links = set()
    for link in matches:
        # Strip common trailing punctuation.
        # This is a heuristic process. The goal is to remove punctuation that is part
        # of the surrounding sentence structure rather than the URL itself.
        # Example: "Check http://example.com." -> "http://example.com"
        # Example: "(link: http://example.com)" -> "http://example.com"

        # List of characters to strip from the end of the link
        # We iterate because there could be multiple, e.g., "http://example.com)."
        # Be careful with characters that can legitimately be part of a URL ending,
        # though less common for these specific ones when they are truly *trailing*.
        punctuation_to_strip = ['.', ',', ';', ':', '!', '?', ')', ']', '}', '>']

        stripped_link = link
        while stripped_link and stripped_link[-1] in punctuation_to_strip:
            # Special handling for parentheses: only strip a trailing ')' if there isn't
            # a corresponding '(' within the path/query part of the URL,
            # or if the count of '(' is less than ')' in the path.
            if stripped_link.endswith(')'):
                path_part = stripped_link.split("://", 1)[-1] if "://" in stripped_link else stripped_link
                if path_part.count('(') < path_part.count(')'):
                     stripped_link = stripped_link[:-1]
                else:
                    # Number of '(' is >= number of ')', so this ')' might be part of a balanced pair or internal.
                    break
            else:
                stripped_link = stripped_link[:-1]

        if stripped_link: # Ensure the link is not empty after stripping
            cleaned_links.add(stripped_link)

    return list(cleaned_links)
