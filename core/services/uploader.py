import os, subprocess, tempfile
from datetime import datetime
from core.utils.config import GITHUB_TOKEN, DEFAULT_REPO
from core.utils.userdb import get_user

def update_subscriptions(user_id: int, links: list[str]):
    user = get_user(user_id)
    repo_name = user.get('repo_name') or DEFAULT_REPO
    token = user.get('github_token') or GITHUB_TOKEN # User specific token takes precedence

    if not repo_name:
        # logging.error(f"User {user_id}: Repository name not configured.")
        print(f"User {user_id}: Repository name not configured.") # Placeholder for logging
        return
    if not token:
        # logging.error(f"User {user_id}: GitHub token not configured.")
        print(f"User {user_id}: GitHub token not configured.") # Placeholder for logging
        return

    # Construct repo_url: token should be part of it for https cloning if it's a PAT
    # The format is https://<token>@github.com/<username>/<repo>.git
    # Or, if SSH is used, it's different, but PATs are typically for HTTPS.
    # Assuming repo_name is in format "username/reponame"
    repo_url = f"https://{token}@github.com/{repo_name}.git"
    # If repo_name already includes user (e.g. from DEFAULT_REPO which might be full name)
    # this might result in https://TOKEN@github.com/OWNER/REPO.git which is correct.

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Clone the specific branch if specified, otherwise default branch
            # For simplicity, let's assume default branch for now.
            # Consider shallow clone if history is not needed: --depth 1
            subprocess.run(['git','clone','--depth','1', repo_url, tmpdir], check=True, capture_output=True, text=True)
            # logging.info(f"User {user_id}: Cloned {repo_name} to {tmpdir}")
            print(f"User {user_id}: Cloned {repo_name} to {tmpdir}")
        except subprocess.CalledProcessError as e:
            # logging.error(f"User {user_id}: Failed to clone {repo_name}. Error: {e.stderr}")
            print(f"User {user_id}: Failed to clone {repo_name}. Error: {e.stderr}")
            return

        # Define the output directory for subscription files within the cloned repo
        # Standardizing to 'subs/' or 'subscriptions/' inside the data_dir is good.
        # The README mentions 'data/subs/'
        subs_output_dir = os.path.join(tmpdir, 'data', 'subs')
        os.makedirs(subs_output_dir, exist_ok=True)

        # build files using the builder service
        from core.services.builder import build_sub_files # Local import to avoid circular deps if any
        build_sub_files(links, subs_output_dir)
        # logging.info(f"User {user_id}: Subscription files built in {subs_output_dir}")
        print(f"User {user_id}: Subscription files built in {subs_output_dir}")

        # Check for changes using git status
        status_result = subprocess.run(['git','-C', tmpdir, 'status', '--porcelain'], check=True, capture_output=True, text=True)
        if not status_result.stdout.strip():
            # logging.info(f"User {user_id}: No changes to commit in {repo_name}.")
            print(f"User {user_id}: No changes to commit in {repo_name}.")
            return

        # Add, commit, and push changes
        try:
            # Configure git user for commit, can be generic
            subprocess.run(['git','-C', tmpdir, 'config', 'user.name', 'Telegram Subscription Bot'], check=True)
            subprocess.run(['git','-C', tmpdir, 'config', 'user.email', 'bot@example.com'], check=True)

            subprocess.run(['git','-C', tmpdir, 'add', '.'], check=True)
            commit_message = f"Update subscription files - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            subprocess.run(['git','-C', tmpdir, 'commit', '-m', commit_message], check=True, capture_output=True, text=True)
            # logging.info(f"User {user_id}: Committed changes to {repo_name} with message: {commit_message}")
            print(f"User {user_id}: Committed changes to {repo_name} with message: {commit_message}")

            # Push to the default branch (usually main or master)
            subprocess.run(['git','-C', tmpdir, 'push'], check=True, capture_output=True, text=True)
            # logging.info(f"User {user_id}: Successfully pushed changes to {repo_name}")
            print(f"User {user_id}: Successfully pushed changes to {repo_name}")

        except subprocess.CalledProcessError as e:
            # logging.error(f"User {user_id}: Git operation failed for {repo_name}. Error: {e.stderr}")
            # Consider logging e.stdout as well for more context
            print(f"User {user_id}: Git operation failed for {repo_name}. Error: {e.stderr}")
        except Exception as e:
            # logging.error(f"User {user_id}: An unexpected error occurred during git operations for {repo_name}: {e}")
            print(f"User {user_id}: An unexpected error occurred during git operations for {repo_name}: {e}")

# Placeholder for get_action_status - to be implemented or removed
# def get_action_status(user_id: int) -> str:
# user = get_user(user_id)
# repo_name = user.get('repo_name') or DEFAULT_REPO
# token = user.get('github_token') or GITHUB_TOKEN
# if not repo_name:
# return "Repository not configured."
#    # This would involve making API calls to GitHub
#    # e.g., using the 'requests' library and the GitHub Actions API
#    # https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28
#    # Needs error handling, parsing response, etc.
# return f"Fetching status for {repo_name} is not yet implemented."
```

The initial content provided in the prompt for `uploader.py` was minimal. I've fleshed it out above based on the requirements and common practices for such a script. I will use this more detailed version for the `create_file_with_block` call.
