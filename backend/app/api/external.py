from fastapi import APIRouter

router = APIRouter()


@router.get("/offers/{token}")
def get_offer(token: str):
    return {"token": token, "status": "PENDING"}


@router.post("/offers/{token}/accept")
def accept_offer(token: str):
    return {"status": "ok"}
