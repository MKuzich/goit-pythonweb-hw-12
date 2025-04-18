from fastapi import Depends, HTTPException, status
from src.repository.database.models import UserRole
from src.services.auth import get_current_user

def require_admin(current_user = Depends(get_current_user)):
    """
    Dependency to ensure the user has admin privileges.

    :param current_user: The current user object.
    :return: The current user if they are an admin.
    :raises HTTPException: If the user is not an admin.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )
    return current_user