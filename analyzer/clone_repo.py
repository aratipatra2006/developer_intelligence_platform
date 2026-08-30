import os
import shutil
import stat
import time

from git import Repo
from git.exc import GitCommandError


CLONE_PATH = "repositories"


def _remove_readonly(func, path, exc_info):
    """
    Remove a read-only file on Windows and retry the operation.
    """
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        os.chmod(path, stat.S_IWRITE)
        func(path)


def _remove_directory(path, retries=3):
    """
    Safely remove a directory, including read-only Git files.

    Returns:
        True if removed or already absent.
        False if removal failed.
    """
    if not os.path.exists(path):
        return True

    for attempt in range(1, retries + 1):
        try:
            shutil.rmtree(
                path,
                onerror=_remove_readonly,
            )
            return True

        except OSError as exc:
            if attempt == retries:
                print(
                    f"⚠️ Could not remove directory "
                    f"after {retries} attempts: {path}"
                )
                print(f"   Reason: {exc}")
                return False

            time.sleep(1)

    return False


def clone_repository(repo_url):
    """
    Clone a GitHub repository into the temporary repositories directory.

    Repositories are treated as temporary working data.

    Features:
        - shallow clone
        - disables Git LFS smudge/downloads
        - removes stale/partial clones
        - handles Windows-invalid paths
        - handles Windows filename-length failures
        - cleans failed partial clones
    """

    repo_path = None

    try:
        os.makedirs(
            CLONE_PATH,
            exist_ok=True,
        )

        # --------------------------------------------------------
        # Normalize URL
        # --------------------------------------------------------

        repo_url = str(repo_url).strip().rstrip("/")

        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]

        parts = repo_url.split("/")

        if len(parts) < 2:
            raise ValueError(
                f"Invalid repository URL: {repo_url}"
            )

        owner = parts[-2].strip()
        repo = parts[-1].strip()

        if not owner or not repo:
            raise ValueError(
                f"Invalid repository URL: {repo_url}"
            )

        # --------------------------------------------------------
        # Local clone path
        # --------------------------------------------------------

        folder_name = f"{owner}_{repo}".lower()

        repo_path = os.path.join(
            CLONE_PATH,
            folder_name,
        )

        # --------------------------------------------------------
        # Remove stale/partial clone
        # --------------------------------------------------------

        if os.path.exists(repo_path):
            print(
                f"Removing existing clone: {repo_path}"
            )

            if not _remove_directory(repo_path):
                return (
                    False,
                    "existing_clone_cleanup_failed",
                )

        # --------------------------------------------------------
        # Prevent Git LFS from downloading large objects
        # --------------------------------------------------------

        previous_lfs_setting = os.environ.get(
            "GIT_LFS_SKIP_SMUDGE"
        )

        os.environ["GIT_LFS_SKIP_SMUDGE"] = "1"

        try:
            Repo.clone_from(
                repo_url,
                repo_path,
                depth=1,
            )

        finally:
            # Restore previous environment setting.
            if previous_lfs_setting is None:
                os.environ.pop(
                    "GIT_LFS_SKIP_SMUDGE",
                    None,
                )
            else:
                os.environ[
                    "GIT_LFS_SKIP_SMUDGE"
                ] = previous_lfs_setting

        print(
            f"✅ Git clone: {repo_url}"
        )

        return True, repo_path

    except GitCommandError as exc:
        error_text = str(exc)
        lowered = error_text.lower()

        # --------------------------------------------------------
        # Classify known Git failures
        # --------------------------------------------------------

        if "invalid path" in lowered:
            reason = "windows_invalid_path"

        elif (
            "filename too long" in lowered
            or "file name too long" in lowered
        ):
            reason = "windows_filename_too_long"

        elif (
            "git-lfs" in lowered
            or "lfs budget" in lowered
            or "smudge filter lfs failed" in lowered
        ):
            reason = "git_lfs_failure"

        elif (
            "repository not found" in lowered
            or "does not exist" in lowered
        ):
            reason = "repository_not_found"

        elif (
            "could not resolve host" in lowered
            or "failed to connect" in lowered
            or "connection timed out" in lowered
        ):
            reason = "network_failure"

        else:
            reason = "git_clone_failure"

        print(
            f"⚠️ {reason}: {repo_url}"
        )

        # Remove partial clone created before checkout failed.
        if repo_path and os.path.isdir(repo_path):
            _remove_directory(repo_path)

        return False, reason

    except Exception as exc:
        error_text = str(exc)

        print(
            f"⚠️ clone_repository failed: "
            f"{repo_url}"
        )
        print(
            f"   {type(exc).__name__}: {error_text}"
        )

        # Remove partial clone if one was created.
        if repo_path and os.path.isdir(repo_path):
            _remove_directory(repo_path)

        return False, error_text