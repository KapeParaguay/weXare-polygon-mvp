from fastapi import Header, HTTPException
import jwt
from jwt import InvalidTokenError
from app.core.config import settings


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing auth")

    token = authorization.replace("Bearer", "").strip()
    if token == "mock" and settings.auth_allow_mock:
        return {
            "id": "user_1",
            "email": "user@example.com",
            "status": "ACTIVE",
            "roles": "CREATOR,WORKER,JUDGE",
        }

    if not settings.privy_verification_key:
        raise HTTPException(status_code=500, detail="Missing PRIVY_VERIFICATION_KEY")

    try:
        key = settings.privy_verification_key.replace("\\n", "\n")
        options = {"verify_aud": bool(settings.privy_app_id)}
        claims = jwt.decode(
            token,
            key,
            algorithms=["ES256", "EdDSA"],
            audience=settings.privy_app_id or None,
            issuer=settings.privy_issuer or None,
            options=options,
        )
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc

    user_id = claims.get("sub") or claims.get("user_id") or claims.get("id")
    email = claims.get("email") or (claims.get("user") or {}).get("email")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing subject")

    return {
        "id": user_id,
        "email": email or "",
        "status": "ACTIVE",
        "roles": "CREATOR,WORKER,JUDGE",
    }
