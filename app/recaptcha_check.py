from fastapi import Request
import httpx
from starlette.exceptions import HTTPException
from fastapi import Form


async def recaptcha_check(request: Request, g_recaptcha_response: str = Form(None)):
    if not g_recaptcha_response:
        raise HTTPException(status_code=400, detail="Ошибка проверки каптчи: токен отсутствует")

    async with httpx.AsyncClient() as client:
        recaptcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"
        data = {
            "secret": "6LfhoQYuAAAAAKg34KXULUSIA-57PCU4T2oIFjJi",  # Секретный ключ из консоли
            "response": g_recaptcha_response,
            "remoteip": request.client.host  # Опционально: IP пользователя
        }
        resp = await client.post(recaptcha_verify_url, data=data)
        result = resp.json()

    if not result.get("success") or result.get("score", 0) < 0.5:
        raise HTTPException(status_code=400, detail="Подозрение на спам")