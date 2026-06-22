from __future__ import annotations

# This class gives the user a token by verifying the username and password.
# This class validates tokens in the header of the request.
# This class doees not handle token generator.

from pathlib import Path
from typing import Union

from Services.Accounts.password_hasher import PasswordHasher
from Services.Accounts.user_manager import UserManager


class AuthenticationService:
    """Handle user credential validation and token-related auth checks."""

    def __init__(self, storage_dir: Union[str, Path] = "."):
        self.user_manager = UserManager(storage_dir)

    def authenticate(self, username: str, password: str) -> bool:
        """Verify the username and password belong to a stored user."""
        if not isinstance(username, str) or not isinstance(password, str):
            return False

        user = self.user_manager.get_user_by_username(username)
        if user is None:
            return False

        return PasswordHasher.verify_password(password, user.get("password_hash", ""))
