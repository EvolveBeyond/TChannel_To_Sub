# Telegram Subscription Bot

This Telegram bot automatically fetches new subscription links from specified Telegram channels, categorizes them, and pushes them to a GitHub repository. It's designed to be run by individual users via GitHub Actions.

## Project Structure

```
telegram-sub-bot/
├── bot.py                      # Main bot entrypoint (handles polling and can trigger updates)
├── run_scheduled_updates.py    # Script for non-interactive subscription updates (used by GitHub Actions)
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables for local development
├── README.md                   # This file
├── .gitignore                  # Specifies intentionally untracked files that Git should ignore
├── data/
│   └── users.json              # Stores user configurations (Telegram ID, channels, optional repo/token)
├── core/
│   ├── handlers/               # Telegram command handlers
│   │   ├── start.py            # Handles /start command
│   │   ├── channels.py         # Handles /tch command (add, remove, list channels)
│   │   ├── github.py           # Handles /status command (placeholder for GitHub Action status)
│   │   └── notify.py           # Module for sending notifications to users
│   ├── services/               # Core business logic
│   │   ├── extractor.py        # (To be implemented) Fetches posts and extracts links from channels
│   │   ├── builder.py          # (To be implemented) Builds subscription files from links
│   │   └── uploader.py         # Clones, updates, and pushes to the user's GitHub subscription repository
│   └── utils/                  # Utility modules
│       ├── userdb.py           # Manages persistence and retrieval of user data from users.json
│       └── config.py           # Loads configuration from environment variables and .env file
└── .github/
    └── workflows/
        └── update.yml          # GitHub Actions workflow for scheduled and manual subscription updates
```

## Local Development

For local development or running the bot outside of GitHub Actions:
1.  Clone your forked repository.
2.  Create a virtual environment: `python -m venv venv` and activate it (`source venv/bin/activate` or `venv\Scripts\activate` on Windows).
3.  Install dependencies: `pip install -r requirements.txt`.
4.  Create a `.env` file in the project root by copying `.env.example`.
5.  Fill in your `BOT_TOKEN`, `GITHUB_TOKEN`, and `DEFAULT_REPO` in the `.env` file.
6.  To run the bot in polling mode (listening for Telegram commands): `python bot.py`
7.  To test the update script locally (simulating an Action run): `python bot.py run_updates`

## How to Use (for GitHub Actions Setup)

To run this bot for yourself, follow these steps:

### 1. Fork the Repository

Click the "Fork" button at the top right of this page to create your own copy of this repository. This will be your **bot repository**.

### 2. Create a Telegram Bot

You'll need a Telegram bot token.
1.  Talk to [BotFather](https://t.me/BotFather) on Telegram.
2.  Use the `/newbot` command.
3.  Follow the instructions to choose a name and username for your bot.
4.  BotFather will give you a **token**. Keep this safe.

### 3. Create a GitHub Personal Access Token

The bot needs a GitHub token to push updates to your subscription repository.
1.  Go to your GitHub [Developer settings](https://github.com/settings/tokens).
2.  Click on "Personal access tokens" -> "Tokens (classic)".
3.  Click "Generate new token" -> "Generate new token (classic)".
4.  Give your token a descriptive name (e.g., `TELEGRAM_SUB_BOT_ACTION`).
5.  Select the **`repo`** scope. This will allow the token to access and write to your repositories.
6.  Click "Generate token" and copy the token. You won't be able to see it again.

### 4. Configure GitHub Secrets in Your Bot Repository

In your forked **bot repository** (the one you created in Step 1), you need to set up secrets for the GitHub Action to use.
1.  Go to your forked bot repository's **Settings** tab.
2.  In the left sidebar, navigate to **Secrets and variables** -> **Actions**.
3.  Click the **New repository secret** button for each of the following secrets:

    *   `BOT_TOKEN`: The Telegram bot token you got from BotFather (Step 2).
    *   `GITHUB_TOKEN`: The GitHub Personal Access Token you created (Step 3). This token will be used by the bot to commit to your subscriptions repository.
    *   `DEFAULT_REPO` (Optional but Recommended): The GitHub repository where the subscription files should be pushed (e.g., `yourusername/my-subscription-links`).
        *   This should be the **full repository name including username**, like `yourusername/my-subs-repo`.
        *   Ensure this repository exists before running the bot or Action. The `uploader.py` script will try to clone it; if the clone fails (e.g., because the repo doesn't exist), the script will error out.
        *   The subscription files will be placed in a `data/subs/` directory within this target repository.
        *   If you don't set this, the bot will expect you to configure the repository name through a bot command (which needs to be fully implemented for setting the repository).

### 5. Enable GitHub Actions

1.  Go to the **Actions** tab in your forked **bot repository**.
2.  If you see a banner saying "Workflows aren't running in this repository" or an "I understand my workflows, go ahead and enable them" button, click it to enable Actions.
3.  The `Update Subscriptions` workflow is defined in `.github/workflows/update.yml`. It's scheduled to run every 6 hours by default. You can also trigger it manually from the Actions tab:
    *   Click on "Update Subscriptions" in the workflows list on the left.
    *   Click the "Run workflow" dropdown button on the right, then "Run workflow".

### 6. Prepare Your Subscription Repository

Create the repository on GitHub that you specified as `DEFAULT_REPO` (e.g., `yourusername/my-subscription-links`). This can be a private or public repository. The bot will clone this repository, add files to a `data/subs/` directory, and push changes. It's crucial this repository exists.

### 7. Start Interacting with Your Bot

1.  Find your bot on Telegram (the one you created with BotFather).
2.  Send the `/start` command.
3.  Use the bot commands to configure it:

## Bot Commands

*   `/start`: Displays a welcome message and lists available commands.
*   `/tch @ChannelNameOrLink`: Adds or removes a Telegram channel to fetch subscription links from.
    *   Examples: `/tch @myawesomesubs` or `/tch https://t.me/publicchannelname`
    *   Examples: `/tch @myawesomesubs` or `/tch https://t.me/publicchannelname`
    *   You can also use `/tch list` to see your current channels and `/tch remove @channel` to remove one.
*   `/status`: Shows a placeholder message for the status of the last GitHub Action run.
    *   *Note: A full implementation for `/status` to show real-time GitHub Actions status would require GitHub API integration and is not yet implemented.*
*   **Configuration Commands (Reliance on GitHub Secrets)**:
    *   User-specific GitHub repository names or tokens are not currently configurable via bot commands.
    *   All GitHub-related configurations (target repository, access token) **must be set via GitHub Secrets** (`DEFAULT_REPO`, `GITHUB_TOKEN`) in your forked bot repository.

## How it Works

1.  **User Interaction (Telegram)**: You interact with your bot on Telegram using commands like `/start` and `/tch`. Your Telegram user ID and chosen channels are stored in `data/users.json` within the bot's repository.
2.  **Scheduled/Manual Updates (GitHub Actions)**:
    *   The GitHub Action defined in `.github/workflows/update.yml` runs on a schedule (default: every 12 hours) or can be manually dispatched from the Actions tab of your bot repository.
    *   **Checkout & Setup**: The workflow checks out the bot's code and sets up the Python environment, installing dependencies from `requirements.txt`.
    *   **Run Update Script**: It executes `python bot.py run_updates`. This command tells `bot.py` to invoke the `main()` function from `run_scheduled_updates.py`.
3.  **`run_scheduled_updates.py` Logic**:
    *   This script is the core of the automated update process. It does *not* start the Telegram poller.
    *   It loads all user configurations from `data/users.json`.
    *   For each user and their specified channels:
        *   It initializes an `aiogram.Bot` instance using the `BOT_TOKEN` secret.
        *   **Fetch & Extract**: It calls `core.services.extractor.py` (to be implemented) to fetch recent posts from channels and extract subscription links.
        *   **Build Subscriptions**: It calls `core.services.builder.py` (to be implemented) to categorize the extracted links and generate subscription files in various formats (e.g., plain text lists for different protocols).
        *   **Upload to GitHub**: It calls `core.services.uploader.py` (`update_subscriptions` function) which:
            *   Clones the user's target subscription repository (defined by `DEFAULT_REPO` or user-specific settings if ever implemented, using `GITHUB_TOKEN`).
            *   Places the newly generated subscription files into a `data/subs/` directory within the cloned repository.
            *   Commits and pushes any changes.
        *   **Notify User**: After a successful update (or if no new links were found), it uses `core.handlers.notify.py` to send a status message to the user on Telegram.
    *   The script exits after processing all users.
4.  **`core/services/uploader.py` in Detail**:
    *   Uses `asyncio.to_thread` to run `git` commands non-blockingly.
    *   Manages cloning, committing, and pushing to the target repository specified by `DEFAULT_REPO` (or user-specific settings if available) using the `GITHUB_TOKEN`.
    *   Subscription files are placed in a `data/subs/` directory in the target repository.

## Important Considerations & Current Status

*   **Core Logic Implementation Status**:
    *   `core/services/extractor.py`: Logic for fetching posts and extracting links is **to be implemented**.
    *   `core/services/builder.py`: Logic for building various subscription file formats is **to be implemented**.
    *   The overall workflow for scheduled updates depends on the completion of these modules.
*   **GitHub Action Execution**: The setup with `bot.py run_updates` calling `run_scheduled_updates.py` is designed for efficient execution in GitHub Actions, avoiding the start of the Telegram poller.
*   **Error Handling**: Basic error handling is in place in `uploader.py` and `run_scheduled_updates.py`. This can be further improved with more specific error reporting and user notifications for critical failures.
*   **`/status` Command**: Currently provides a static message. Real-time status requires GitHub API integration.
*   **User-Specific GitHub Configuration**: The bot currently relies on `DEFAULT_REPO` and `GITHUB_TOKEN` secrets for all users. Storing and using per-user GitHub tokens or repository names via bot commands is not implemented and would require careful security considerations for token storage.
*   **Security of `data/users.json`**: This file contains Telegram user IDs and their channel lists. If your bot repository is public, this data will also be public. It does *not* (and should not) store GitHub tokens.
*   **Idempotency**: The update process should ideally be idempotent, meaning running it multiple times with the same input should produce the same result in the target repository without causing errors or duplicate entries (e.g., `uploader.py` checks for actual changes before committing).

By forking this repository and following these setup instructions, you can automate the process of collecting and organizing your Telegram subscription links. Development is ongoing, particularly for the link extraction and subscription building services.
