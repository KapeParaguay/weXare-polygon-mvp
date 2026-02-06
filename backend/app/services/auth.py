from fastapi import Header, HTTPException


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    # MVP stub: validate Supabase JWT in production.
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing auth")
    return {
        "id": "user_1",
        "email": "user@example.com",
        "status": "ACTIVE",
        "roles": "CREATOR,WORKER,JUDGE",
    }
