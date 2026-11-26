"""Provision an administrator interactively; roles are never self-selected."""
from getpass import getpass
from backend.database import session_factory
from backend.models import User
from backend.auth import hash_password

def main():
    email = input("Administrator email: ").strip().lower()
    password = getpass("Password (at least 12 characters): ")
    if len(password) < 12:
        raise SystemExit("Password too short")
    with session_factory()() as db:
        if db.query(User).filter_by(email=email).first():
            raise SystemExit("Account already exists")
        db.add(User(username="Administrator", email=email, password=hash_password(password), role="admin"))
        db.commit()
if __name__ == "__main__":
    main()
