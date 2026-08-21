from fastapi import Depends

from app.core.security import get_current_user


async def require_operator(current_user=Depends(get_current_user)):
    """Ensure the current user is an operator or admin."""
    if current_user["role"] not in ("OPERATOR", "ADMIN"):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user
