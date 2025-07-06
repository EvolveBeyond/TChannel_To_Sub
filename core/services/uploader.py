import os
import subprocess
import tempfile
import logging
import asyncio
from datetime import datetime

from core.utils.config import GITHUB_TOKEN, DEFAULT_REPO
from core.utils.userdb import get_user
from core.services.builder import build_sub_files # Ensure this is correctly imported

# Setup logger for this module
logger = logging.getLogger(__name__)

async def run_git_command(cmd: list[str], cwd: str = None, check: bool = True) -> subprocess.CompletedProcess:
    """Helper function to run git commands asynchronously."""
    process = await asyncio.to_thread(
        subprocess.run,
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
        check=check # Will raise CalledProcessError if check is True and command fails
    )
    return process

async def update_subscriptions(user_id: int, links: list[str]) -> bool:
    """
    Clones the user's repository, builds subscription files, and pushes changes.
    Returns True on success, False on failure.
    """
    user = get_user(user_id) # This is synchronous, consider if userdb needs async methods if it becomes a bottleneck
    repo_name = user.get('repo_name') or DEFAULT_REPO
    # User specific token takes precedence if available, otherwise use the global GITHUB_TOKEN
    # Ensure that if user.get('github_token') is an empty string, it falls back to GITHUB_TOKEN
    token = user.get('github_token') if user.get('github_token') else GITHUB_TOKEN


    if not repo_name:
        logger.error(f"User {user_id}: Repository name not configured.")
        return False
    if not token:
        logger.error(f"User {user_id}: GitHub token not configured (neither user-specific nor global).")
        return False

    repo_url = f"https://{token}@github.com/{repo_name}.git"

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            logger.info(f"User {user_id}: Cloning {repo_name} into {tmpdir}")
            try:
                await run_git_command(['git', 'clone', '--depth', '1', repo_url, tmpdir], cwd=None)
                logger.info(f"User {user_id}: Successfully cloned {repo_name}.")
            except subprocess.CalledProcessError as e:
                logger.error(f"User {user_id}: Failed to clone {repo_name}. Error: {e.stderr}")
                return False

            subs_output_dir = os.path.join(tmpdir, 'data', 'subs')
            os.makedirs(subs_output_dir, exist_ok=True)

            logger.info(f"User {user_id}: Building subscription files in {subs_output_dir}")
            # build_sub_files itself is synchronous. If it becomes I/O bound or very CPU intensive,
            # it might also need to be run in a thread. For now, assuming it's acceptable.
            try:
                # This function needs to be robust.
                # It should create files based on the links provided.
                build_sub_files(links, subs_output_dir)
                logger.info(f"User {user_id}: Subscription files built.")
            except Exception as e:
                logger.error(f"User {user_id}: Error building subscription files: {e}", exc_info=True)
                return False


            try:
                status_result = await run_git_command(['git', 'status', '--porcelain'], cwd=tmpdir)
                if not status_result.stdout.strip():
                    logger.info(f"User {user_id}: No changes to commit in {repo_name}.")
                    # Even if no changes, we can consider it a "successful" run in terms of processing
                    # The notification logic can distinguish between "updated" and "no changes".
                    return True
            except subprocess.CalledProcessError as e:
                logger.error(f"User {user_id}: Failed to get git status for {repo_name}. Error: {e.stderr}")
                return False

            logger.info(f"User {user_id}: Changes detected. Proceeding with commit and push for {repo_name}.")
            try:
                await run_git_command(['git', 'config', 'user.name', 'Telegram Subscription Bot'], cwd=tmpdir)
                await run_git_command(['git', 'config', 'user.email', 'bot@example.com'], cwd=tmpdir)
                await run_git_command(['git', 'add', '.'], cwd=tmpdir)

                commit_message = f"Update subscription files - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                await run_git_command(['git', 'commit', '-m', commit_message], cwd=tmpdir)
                logger.info(f"User {user_id}: Committed changes with message: \"{commit_message}\"")

                await run_git_command(['git', 'push'], cwd=tmpdir)
                logger.info(f"User {user_id}: Successfully pushed changes to {repo_name}")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"User {user_id}: Git operation (commit/push) failed for {repo_name}. Error: {e.stderr}")
                if "remote end hung up unexpectedly" in e.stderr or "TLS_ERROR" in e.stderr:
                     logger.error(f"User {user_id}: This might be a TLS/SSL issue with git. Ensure libssl is up to date on the runner or system.")
                return False
            except Exception as e: # Catch any other unexpected errors during git operations
                logger.error(f"User {user_id}: An unexpected error occurred during git operations for {repo_name}: {e}", exc_info=True)
                return False

    except Exception as e: # Catch errors related to TemporaryDirectory or other setup
        logger.error(f"User {user_id}: A critical error occurred in update_subscriptions for {repo_name}: {e}", exc_info=True)
        return False

# Note: The placeholder for get_action_status was removed as it's not directly part of uploader's core responsibility.
# That logic would typically reside in a handler or a separate GitHub API interaction module.