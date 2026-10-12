import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.analytics import register_visit


EXCLUDED_PATHS = {
    "/robots.txt",
    "/sitemap.xml",
    "/favicon.ico",
    "/analytics",
}


class CounterMiddleWare(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        # Считаем только GET-запросы к страницам.
        should_track = (
            request.method == "GET"
            and not request.url.path.startswith("/static/")
            and not request.url.path.startswith("/admin/")
            and request.url.path not in EXCLUDED_PATHS
            and not request.url.path.startswith("/docs")
            and not request.url.path.startswith("/redoc")
            and not request.url.path.startswith("/openapi")
        )

        if not should_track:
            return await call_next(request)

        session_id = request.cookies.get("analytics_session")
        is_new_cookie = not session_id

        if not session_id:
            session_id = str(uuid.uuid4())

        # Не доверяем произвольному X-Forwarded-For напрямую.
        # request.client должен быть корректно настроен через доверенный proxy.
        client_ip = (
            request.client.host
            if request.client
            else ""
        )

        # Не записываем query-параметры: в URL могут быть персональные данные.
        path = request.url.path

        try:
            session_id = register_visit(
                session_id=session_id,
                path=path,
                method=request.method,
                user_agent=request.headers.get("user-agent", ""),
                ip=client_ip,
            )
        except Exception:
            # Сбой аналитики не должен ломать основной сайт.
            import logging
            logging.getLogger(__name__).exception(
                "Не удалось записать посещение"
            )

        response = await call_next(request)

        if is_new_cookie or session_id != request.cookies.get(
            "analytics_session"
        ):
            response.set_cookie(
                key="analytics_session",
                value=session_id,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                secure=True,  # Для production с HTTPS
                samesite="lax",
                path="/",
            )

        return response
