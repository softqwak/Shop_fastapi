from fastapi import HTTPException

from apps.accounts.models import User
from apps.core.date_time import DateTime


class UserManager:
    @staticmethod
    def get_user(user_id: int | None = None, email: str = None) -> User | None:
        """
        Retrieve a user based on their ID or email address.

        Args:
            user_id (int | None): The ID of the user to retrieve. Defaults to None.
            email (str | None): The email address of the user to retrieve. Defaults to None.

        Returns:
            User | None: A User object if a user is found based on the provided ID or email,
                         or None if no user is found.
        """
        if user_id:
            return User.get(user_id)
        elif email:
            return User.filter(User.email == email).first()
        return None

    @staticmethod
    def get_user_or_404(user_id: int | None = None, email: str = None):
        if user_id:
            instance = User.get_or_404(user_id)
        elif email:
            instance = User.filter(User.email == email).first()
            if not instance:
                raise HTTPException(status_code=404, detail=f"User not found")
        return instance

    @staticmethod
    def to_dict(user: User):
        """
        Convert a User object to a dictionary.
        """
        _dict = {
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'verified_email': user.verified_email,
            'date_joined': DateTime.string(user.date_joined),
            'updated_at': DateTime.string(user.updated_at),
            'last_login': DateTime.string(user.last_login)
        }
        return _dict

    @staticmethod
    def new_user(**user_data):
        return User.create(**user_data)
