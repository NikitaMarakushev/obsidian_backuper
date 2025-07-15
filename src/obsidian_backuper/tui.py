from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Button, Header, Footer, Static, Input, Label, ProgressBar
from textual import on, work
from pathlib import Path
from typing import Optional
import os

from .core import ObsidianBackuper
from .obsidian_decryptor import ObsidianDecryptor
from .exceptions import (
    ObsidianBackupError,
    VaultValidationError,
    EncryptionError,
    DecryptionError
)


class OperationComplete(Static):
    """Display a success message when operation completes."""


class ObsidianBackupTUI(App):
    """A Textual TUI for Obsidian Backuper."""

    CSS_PATH = "style/tui.css"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Label("Obsidian Backup Tool", id="title"),
                Label("Vault Path:", classes="input-label"),
                Input(placeholder="Path to vault or encrypted file", id="vault-path"),
                Label("Password:", classes="input-label"),
                Input(placeholder="Encryption/decryption password", password=True, id="password"),
                Horizontal(
                    Button("Encrypt Backup", variant="primary", id="encrypt"),
                    Button("Decrypt Backup", variant="warning", id="decrypt"),
                    id="buttons"
                ),
                ProgressBar(show_eta=False, id="progress"),
                OperationComplete("", id="operation-complete"),
                id="main-container"
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        self.title = "Obsidian Backup Tool"
        self.sub_title = "Python 3.12"
        self.query_one("#progress").display = False
        self.query_one("#operation-complete").display = False

    @on(Button.Pressed, "#encrypt")
    def handle_encrypt(self) -> None:
        """Handle encrypt button press."""
        self.run_backup_operation(encrypt=True)

    @on(Button.Pressed, "#decrypt")
    def handle_decrypt(self) -> None:
        """Handle decrypt button press."""
        self.run_backup_operation(encrypt=False)


    @work(thread=True)
    def run_backup_operation(self, encrypt: bool) -> None:
        """Run the backup operation in a worker thread."""
        vault_path = self.query_one("#vault-path", Input).value
        password = self.query_one("#password", Input).value

        if not vault_path:
            self.notify("Vault path is required!", severity="error")
            return

        if not password:
            self.notify("Password is required!", severity="error")
            return

        self.call_from_thread(
            self.update_ui_for_operation_start,
            f"{'Encrypting' if encrypt else 'Decrypting'}..."
        )

        try:
            if encrypt:
                backuper = ObsidianBackuper(vault_path)
                backup_path = backuper.create_backup(
                    encrypt=True,
                    password=password
                )
                success_message = f"Encrypted backup created at:\n{backup_path}"
            else:
                decryptor = ObsidianDecryptor(vault_path)
                decrypted_path = decryptor.decrypt(password=password)
                success_message = f"File decrypted to:\n{decrypted_path}"

            # Update UI for success
            self.call_from_thread(
                self.update_ui_for_success,
                success_message
            )

        except VaultValidationError as e:
            self.call_from_thread(self.notify, f"Vault error: {str(e)}", severity="error")
        except (EncryptionError, DecryptionError) as e:
            self.call_from_thread(self.notify, f"Crypto error: {str(e)}", severity="error")
        except ObsidianBackupError as e:
            self.call_from_thread(self.notify, f"Backup error: {str(e)}", severity="error")
        except Exception as e:
            self.call_from_thread(self.notify, f"Unexpected error: {str(e)}", severity="error")
        finally:
            self.call_from_thread(self.update_ui_for_operation_end)

    def update_ui_for_operation_start(self, message: str) -> None:
        """Update UI when operation starts."""
        progress = self.query_one("#progress", ProgressBar)
        progress.update(total=100, progress=0)
        progress.display = True
        self.query_one("#operation-complete", OperationComplete).display = False
        self.query_one("#buttons", Horizontal).disabled = True
        self.notify(message)

    def update_ui_for_success(self, message: str) -> None:
        """Update UI when operation succeeds."""
        operation_complete = self.query_one("#operation-complete", OperationComplete)
        operation_complete.update(message)
        operation_complete.display = True
        self.notify("Operation completed successfully!", severity="success")

    def update_ui_for_operation_end(self) -> None:
        """Update UI when operation ends (success or failure)."""
        self.query_one("#progress", ProgressBar).display = False
        self.query_one("#buttons", Horizontal).disabled = False


def run_tui():
    """Run the TUI application."""
    app = ObsidianBackupTUI()
    app.run()