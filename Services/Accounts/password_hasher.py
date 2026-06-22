# Creates password hashes and verifies passwords. Useing hashlib
# Bcrypt is the better library for this but for the sake of simplicity I am using hashlib.

import hashlib
import hmac
import os
import binascii


class PasswordHasher:
    """Password hashing helper using hashlib.pbkdf2_hmac."""

    SALT_SIZE = 16
    HASH_NAME = "sha256"
    ITERATIONS = 100_000
    KEY_LENGTH = 32

    @staticmethod
    def hash_password(password: str) -> str:
        """Return a salted password hash string for storage."""
        if not isinstance(password, str):
            raise TypeError("password must be a string")

        salt = os.urandom(PasswordHasher.SALT_SIZE)
        key = hashlib.pbkdf2_hmac(
            PasswordHasher.HASH_NAME,
            password.encode("utf-8"),
            salt,
            PasswordHasher.ITERATIONS,
            dklen=PasswordHasher.KEY_LENGTH,
        )
        return (
            f"{PasswordHasher.HASH_NAME}${PasswordHasher.ITERATIONS}"
            f"${binascii.hexlify(salt).decode()}"
            f"${binascii.hexlify(key).decode()}"
        )

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify a password against a stored hash string."""
        if not isinstance(password, str):
            raise TypeError("password must be a string")
        if not isinstance(stored_hash, str):
            raise TypeError("stored_hash must be a string")

        try:
            hash_name, iterations, salt_hex, key_hex = stored_hash.split("$", 3)
            iterations = int(iterations)
            salt = binascii.unhexlify(salt_hex)
            stored_key = binascii.unhexlify(key_hex)
        except (ValueError, TypeError, binascii.Error):
            return False

        new_key = hashlib.pbkdf2_hmac(
            hash_name,
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=len(stored_key),
        )
        return hmac.compare_digest(new_key, stored_key)
