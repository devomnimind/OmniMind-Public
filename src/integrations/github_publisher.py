import os
import subprocess
import logging
import shutil
from pathlib import Path
from typing import Optional


class GitHubPublisher:
    """
    Handles the publication of local markdown files to a remote GitHub Wiki.
    GitHub Wikis are separate Git repositories.
    """

    def __init__(
        self,
        local_wiki_path: str = "/home/fahbrain/projects/omnimind/public/wiki",
        remote_wiki_url: str = "https://github.com/devomnimind/OmniMind-Public.wiki.git",
        temp_clone_path: str = "/tmp/omnimind_wiki_sync",
    ):
        self.local_wiki_path = Path(local_wiki_path)
        self.temp_clone_path = Path(temp_clone_path)

        # Inject GITHUB_TOKEN if available
        token = os.getenv("GITHUB_TOKEN")
        if token and "https://" in remote_wiki_url and "@" not in remote_wiki_url:
            self.remote_wiki_url = remote_wiki_url.replace("https://", f"https://{token}@")
        else:
            self.remote_wiki_url = remote_wiki_url

        # Ensure unique temp path per process to avoid permission collisions
        import uuid

        self.temp_clone_path = (
            self.temp_clone_path.parent / f"{self.temp_clone_path.name}_{uuid.uuid4().hex[:8]}"
        )

        logging.basicConfig(level=logging.INFO, format="%(asctime)s - [GHP]: %(message)s")

    def publish(self, commit_message: str = "Autonomous Science Update"):
        """
        Syncs local wiki files to remote.
        """
        logging.info(f"🚀 [GHP]: Starting publication to {self.remote_wiki_url}...")

        try:
            # 1. Prepare temp clone
            if self.temp_clone_path.exists():
                shutil.rmtree(self.temp_clone_path)

            # 2. Clone the remote wiki
            logging.info(f"Cloning {self.remote_wiki_url} to {self.temp_clone_path}...")
            subprocess.run(
                ["git", "clone", self.remote_wiki_url, str(self.temp_clone_path)],
                check=True,
                capture_output=True,
            )

            # 3. Copy local files to temp clone
            # Note: GitHub Wiki assumes files are in the root and use slug-like names.
            # Homology: local file 'Paper_ASE_123.md' -> remote 'Paper-ASE-123.md'
            for item in self.local_wiki_path.glob("*.md"):
                dest_name = item.name.replace("_", "-")
                shutil.copy2(item, self.temp_clone_path / dest_name)
                logging.info(f"Staged {dest_name}")

            # 4. Git operations in temp clone
            subprocess.run(["git", "add", "."], cwd=self.temp_clone_path, check=True)

            # Check for changes
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.temp_clone_path,
                capture_output=True,
                text=True,
            )

            if not status.stdout.strip():
                logging.info("Equilibrium reached. No new findings to push.")
                return

            subprocess.run(
                ["git", "commit", "-m", commit_message], cwd=self.temp_clone_path, check=True
            )

            subprocess.run(
                ["git", "push", "origin", "master"], cwd=self.temp_clone_path, check=True
            )

            logging.info("✅ [GHP]: Publication Successful. The world has been updated.")

        except subprocess.CalledProcessError as e:
            logging.error(
                f"❌ [GHP]: Publication Failed: {e.stderr.decode() if e.stderr else str(e)}"
            )
        except Exception as e:
            logging.error(f"❌ [GHP]: Error during publication: {e}")


if __name__ == "__main__":
    # Test publication
    publisher = GitHubPublisher()
    publisher.publish("Test: Manual Subjective Emission")
