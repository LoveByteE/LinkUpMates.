# utils/security.py
# Password helpers. We never store the real password, only a hash of it.
import bcrypt


def hash_password(password: str) -> str:
    # bcrypt adds a random "salt" for us, so two identical passwords get different hashes
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    # checks a typed password against the stored hash
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
