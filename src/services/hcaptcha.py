from httpx import AsyncClient

from src.conf.config import settings

verify_url = "https://api.hcaptcha.com/siteverify"


async def verify(h_captcha_response: str) -> bool:
    if not settings.hcaptcha_enabled:
        return True
    data = {
        "response": h_captcha_response,
        "secret": settings.hcaptcha_secret_key,
        "sitekey": settings.hcaptcha_site_key,
    }
    async with AsyncClient(base_url=verify_url) as ac:
        response = await ac.post("/", data=data)
        result = response.json()
        return result["success"] if response.status_code == 200 else False
