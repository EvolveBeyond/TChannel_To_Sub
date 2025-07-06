# Telegram Subscription Bot

This Telegram bot automatically fetches V2Ray, Trojan, Shadowsocks, and other proxy links from specified Telegram channels. It then categorizes these links and generates subscription files suitable for various clients and tools, including Hiddify, NPV Tunnel, ClashMeta, and general Xray-compatible applications. The bot pushes these generated files to a user-configured GitHub repository and is designed to be run by individual users via GitHub Actions.

## Project Structure

```
telegram-sub-bot/
├── bot.py                      # Bot entrypoint
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables
├── README.md                   # This file
├── data/
│   ├── users.json              # Per-user settings (channels, tokens, repo) - created automatically
│   └── subs/                   # Generated subscription files - created automatically in your target repo
├── core/
│   ├── handlers/               # Telegram handlers
│   │   ├── start.py            # /start and main menu
│   │   ├── github.py           # GitHub settings and status
│   │   ├── channels.py         # /tch command for managing channels
│   │   └── notify.py           # Notify user when subs update (placeholder)
│   ├── services/               # Business logic
│   │   ├── extractor.py        # Fetch and parse channel posts
│   │   ├── builder.py          # Build subs in all formats dynamically
│   │   └── uploader.py         # Clone, commit, push to GitHub
│   └── utils/                  # Low-level utilities
│       ├── userdb.py           # Persist and retrieve user data
│       └── config.py           # Load environment variables
└── .github/
    └── workflows/
        └── update.yml         # GitHub Actions: schedule and dispatch
```

## How to Use

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

Create **your own personal or dedicated** repository on GitHub that you specified as `DEFAULT_REPO` (e.g., `yourusername/my-subscription-links`). This will be **your subscription repository**. It can be private or public. The bot will clone this repository, add files to a `data/subs/` directory, and push changes. It's crucial this repository exists.

### 7. Start Interacting with Your Bot

1.  Find your bot on Telegram (the one you created with BotFather).
2.  Send the `/start` command.
3.  Use the bot commands to configure it:

## Bot Commands

*   `/start`: Displays a welcome message and lists available commands.
*   `/tch @ChannelNameOrLink`: Adds or removes a Telegram channel to fetch subscription links from.
    *   Examples: `/tch @myawesomesubs` or `/tch https://t.me/publicchannelname`
    *   When you add a channel, the bot will immediately try to fetch links from the last 50 posts and update your subscription repository (if `DEFAULT_REPO` and `GITHUB_TOKEN` are correctly set up).
*   `/status`: Shows the status of the last GitHub Action run.
    *   *Note: The function `get_action_status` in `core/handlers/github.py` is a placeholder. For this to work, it needs to be implemented to fetch actual GitHub Actions workflow run status using the GitHub API. This would likely involve querying workflow runs in your bot repository or inspecting commit history in the target subscription repository.*
*   **Configuration Commands (Currently reliant on `DEFAULT_REPO` secret)**:
    *   The system is designed to potentially store user-specific GitHub repository names and tokens in `data/users.json` (see `core/utils/userdb.py`).
    *   However, the Telegram command handlers in `core/handlers/github.py` do not currently include commands for users to *set* these details (e.g., `/setrepo yourusername/your-subs-repo` or `/settoken <your_pat>`).
    *   Therefore, configuration **must currently be done using the `DEFAULT_REPO` GitHub Action secret**.

## How it Works

1.  **User Interaction (Telegram)**: You interact with your bot on Telegram using commands like `/start` and `/tch`.
2.  **Data Storage (`data/users.json`)**:
    *   When you use `/tch`, your Telegram user ID and the list of your specified channels are saved in `data/users.json`. This file is located in the `data/` directory within the **bot's repository** (the one you forked).
    *   This `users.json` file is used by the GitHub Action to know which channels to process.
3.  **Scheduled Updates (GitHub Actions)**:
    *   The GitHub Action defined in `.github/workflows/update.yml` runs on a schedule (default: every 6 hours) or when manually dispatched.
    *   **Checkout**: It checks out the latest code of your **bot repository**.
    *   **Setup**: It sets up Python and installs dependencies from `requirements.txt`.
    *   **Run Update Script**: It executes `python scheduled_update.py` (located in the root of the bot repository) using the `BOT_TOKEN`, `GITHUB_TOKEN`, and `DEFAULT_REPO` secrets. This script is specifically designed for non-interactive, scheduled execution:
        *   It loads all user configurations from `data/users.json`.
        *   For each user, it fetches links from all their subscribed channels.
        *   It then calls the necessary services to build and upload the subscription files to the user's designated GitHub repository.
4.  **Subscription Fetching, Processing, and File Generation**:
    *   `core/services/extractor.py`: Fetches recent messages from the specified Telegram channels and extracts all URI (Uniform Resource Identifier) links.
    *   `core/services/builder.py`: Takes the extracted links and categorizes them based on their protocol (e.g., `vmess://`, `vless://`, `trojan://`, `ss://`). It then generates several `.txt` files in the `data/subs/` directory of your target subscription repository:
        *   **Protocol-specific files**:
            *   `vmess.txt`: Contains only VMESS links.
            *   `vless.txt`: Contains only VLESS links. (Primarily for Hiddify, but usable by other Xray clients)
            *   `trojan.txt`: Contains only Trojan links. (For NPV Tunnel and other clients)
            *   `shadowsocks.txt`: Contains only Shadowsocks (ss://) links.
            *   `shadowsocksr.txt`: Contains only ShadowsocksR (ssr://) links.
            *   `tuic.txt`: Contains only TUIC links.
            *   `hysteria.txt`: Contains only Hysteria (v1) links.
            *   `hysteria2.txt`: Contains only Hysteria2 (hy2://) links.
        *   **Aggregated file**:
            *   `all_proxies.txt`: Contains all unique links that were successfully identified and categorized from the known protocols listed above. This file is useful for clients like ClashMeta or any tool that can consume a list of mixed proxy types.
        *   **Fallback file**:
            *   `clashMetaCore.txt`: Contains any links that did not match the explicitly defined protocols in `FORMAT_MAP`. This can be useful for experimental or less common link types.
    *   **Client Compatibility**:
        *   **Hiddify**: Primarily use `vless.txt`. Hiddify apps can often import other types as well.
        *   **NPV Tunnel**: Use `trojan.txt`.
        *   **Xray-compatible clients** (e.g., V2RayN, NekoBox, Streisand, etc.): Use the specific protocol files (`vmess.txt`, `vless.txt`, `trojan.txt`, `shadowsocks.txt`) as needed.
        *   **ClashMeta**: Use `all_proxies.txt` for a comprehensive list, or combine specific protocol files. The individual files can also be used as separate proxy providers in Clash.

5.  **Pushing to GitHub (Subscription Repository)**:
    *   `core/services/uploader.py`: This service handles the Git operations.
        *   It clones your target subscription repository (e.g., `yourusername/my-subs-repo` specified in `DEFAULT_REPO` or user settings) into a temporary directory using the `GITHUB_TOKEN` (your Personal Access Token) for authentication over HTTPS.
        *   It places the newly generated subscription files (e.g., `vmess.txt`, `all_proxies.txt`) into the `data/subs/` directory within this cloned repository. If these files already exist, they are overwritten with the latest links.
        *   It then uses Git commands to add any changes, commit them with a timestamp, and push them back to your subscription repository.

## Important Considerations & Current Limitations

*   **GitHub Action Execution**: The scheduled updates are handled by `scheduled_update.py`, which is designed for this purpose. The `bot.py` script is for interactive Telegram polling only.
*   **Error Handling**: The `subprocess.run` calls in `uploader.py` use `check=True`. This is good for stopping on errors, but more specific error handling (e.g., logging failures for specific channels, or if a GitHub push fails) and potentially notifying the user via Telegram would improve robustness.
*   **GitHub API for `/status`**: The `/status` command's `get_action_status` function in `core/handlers/github.py` is a placeholder. A full implementation would need to query the GitHub API for the status of workflow runs in the bot repository.
*   **User-Specific GitHub Configuration via Bot**: The handlers for setting custom GitHub repository/token per user are not implemented. Users must rely on the `DEFAULT_REPO` secret for now.
*   **Initial `users.json`**: The `data/users.json` file is created if it doesn't exist but starts empty. The first interaction via `/tch` for any user will create their entry.
*   **Security of `data/users.json`**: This file, containing Telegram user IDs and their subscribed channel list, is stored within your bot's repository. If this repository is public, this information will be public. It does *not* (and should not) store GitHub tokens.

By forking this repository and following these setup instructions, you can automate the process of collecting and organizing your Telegram subscription links. Remember to review the "Important Considerations" for potential improvements, especially regarding the GitHub Action execution logic for scheduled updates.
