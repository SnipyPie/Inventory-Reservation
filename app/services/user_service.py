from argon2 import PasswordHasher
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import engine
from app.models.user import User
from argon2.exceptions import VerificationError, VerifyMismatchError
from email_validator import EmailNotValidError, validate_email
from app.models.wallet import Wallet

_password_hasher = PasswordHasher()


def register_user(email: str, password: str):
    """
    registering a new user, checks if the user exists then won't register"""

    email = _normalize_email(email)

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    with Session(engine) as session:
        existing_user = session.scalar(
            select(User).where(User.email == email)
        )

        if existing_user is not None:
            raise ValueError("An account with that email already exists.")

        user = User(
            email=email,
            password_hash=_password_hasher.hash(password),
        )

        session.add(user)
        session.flush()

        wallet = Wallet(user_id=user.id)
        session.add(wallet)

        session.commit()
        session.refresh(user)
        return user

def authenticate_user(email: str, password: str):
    email = _normalize_email(email)

    with Session(engine) as session:
        user = session.scalar(
            select(User).where(User.email == email)
        )

        if user is None:
            return None, "not_found"

        try:
            _password_hasher.verify(user.password_hash, password)
        except VerifyMismatchError:
            return None, "wrong_password"
        except VerificationError:
            return None, "invalid_hash"

        return user, "authenticated"

def _normalize_email(email: str) -> str:
    """
    Verifies if the email is valid format or not"""
    email = email.strip()

    if not email:
        raise ValueError("Email cannot be empty.")

    try:
        result = validate_email(email, check_deliverability=False)
        return result.normalized
    except EmailNotValidError as error:
        raise ValueError(str(error)) from error