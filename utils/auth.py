import bcrypt
from storage.chat_db import add_user, validate_user

def hash_password(password: str) -> str:
    """Zwraca bezpieczny hash hasła."""
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()

def check_password(password: str, hashed: str) -> bool:
    """Sprawdza poprawność hasła względem zahashowanej wersji."""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(username: str, password: str) -> bool:
    """
    Rejestruje nowego użytkownika.
    Zwraca True jeśli sukces, False jeśli użytkownik już istnieje.
    """
    password_hash = hash_password(password)
    return add_user(username, password_hash)

def authenticate_user(username: str, password: str) -> bool:
    """
    Weryfikuje użytkownika przy logowaniu (hasło).
    """
    user = validate_user(username)
    if not user:
        return False

    stored_hash, _ = user
    return check_password(password, stored_hash)