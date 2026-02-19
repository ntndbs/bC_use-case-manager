"""FastAPI dependencies for authentication and authorization."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import decode_access_token
from db.database import get_db
from db.models import User, Role

security_scheme = HTTPBearer()

# Role hierarchy: ADMIN > MAINTAINER > READER
ROLE_LEVEL = {
    Role.READER: 0,
    Role.MAINTAINER: 1,
    Role.ADMIN: 2,
}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT, return the User from DB."""
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def require_role(min_role: Role):
    """Dependency factory: ensures current user has at least `min_role`."""

    async def _check(user: User = Depends(get_current_user)) -> User:
        if ROLE_LEVEL.get(user.role, -1) < ROLE_LEVEL[min_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role {min_role.value} or higher",
            )
        return user

    return _check
