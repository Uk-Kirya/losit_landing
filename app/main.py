from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import (
    RedirectResponse,
    FileResponse,
    HTMLResponse,
)

from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.mailer import send_email

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Proxy headers
app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts=["*"]
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request, exc):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            '404.html',
            {
                "request": request
            },
            status_code=404
        )
    return templates.TemplateResponse(
        '500.html',
        {
            "request": request,
            "status_code": exc.status_code
        },
        status_code=exc.status_code
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    return templates.TemplateResponse(
        '500.html',
        {
            "request": request
        },
        status_code=500
    )


@app.get(
    path='/',
    response_class=HTMLResponse,
    summary="Главная страница",
    include_in_schema=False,
    name='home',
    tags=["Веб-сайт"]
)
async def index_page(
    request: Request,
) -> HTMLResponse:
    """
    Главная страница
    :param request: Request Object
    :return: HTMLResponse Object
    """
    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
        }
    )


@app.get(
    '/policy',
    response_class=HTMLResponse,
    summary='Страница с политикой конфиденциальности',
    include_in_schema=False,
    name='policy',
    tags=["Веб-сайт"]
)
async def get_policy(
    request: Request
) -> HTMLResponse:
    """
    Страница политика конфиденциальности
    :param request: Request Object
    :return: HTMLResponse Object
    """

    return templates.TemplateResponse(
        'policy.html',
        {
            'request': request,
        }
    )


@app.get(
    '/about',
    response_class=HTMLResponse,
    summary='Информация о самозанятом',
    include_in_schema=False,
    name='about',
    tags=["Веб-сайт"]
)
async def get_about(
    request: Request
) -> HTMLResponse:
    """
    Информация о самозанятом
    :param request: Request Object
    :return: HTMLResponse Object
    """

    return templates.TemplateResponse(
        'about.html',
        {
            'request': request,
        }
    )


@app.get(
    '/programm',
    response_class=HTMLResponse,
    summary='Программа курсов',
    include_in_schema=False,
    name='programm',
    tags=["Веб-сайт"]
)
async def get_programm(
    request: Request
) -> HTMLResponse:
    """
    Страница политика конфиденциальности
    :param request: Request Object
    :return: HTMLResponse Object
    """

    return templates.TemplateResponse(
        'programm.html',
        {
            'request': request,
        }
    )


@app.get(
    '/success',
    response_class=HTMLResponse,
    summary='Заявка отправлена',
    include_in_schema=False,
    tags=["Веб-сайт"]
)
async def success(
    request: Request
) -> HTMLResponse:
    """
    Заявка отправлена
    :param request: Request Object
    :return: HTMLResponse Object
    """

    return templates.TemplateResponse(
        'success.html',
        {
            'request': request,
        }
    )


@app.get(
    "/robots.txt",
    response_class=FileResponse,
    summary="Файл robots.txt",
    include_in_schema=False,
    tags=["Веб-сайт"],
)
async def robots_txt(request: Request) -> FileResponse:
    """
    Отдаёт robots.txt
    :param request: Request Object
    :return: FileResponse Object
    """
    return FileResponse(
        path=STATIC_DIR / "robots.txt",
        media_type="text/plain",
    )


@app.get(
    "/sitemap.xml",
    response_class=FileResponse,
    summary="Файл sitemap.xml",
    include_in_schema=False,
    tags=["Веб-сайт"],
)
async def sitemap_xml(request: Request) -> FileResponse:
    """
    Отдаёт sitemap.xml
    :param request: Request Object
    :return: FileResponse Object
    """
    return FileResponse(
        path=STATIC_DIR / "sitemap.xml",
        media_type="application/xml",
    )


@app.get(
    "/yandex_63e4078520e2fe9d.html",
    response_class=FileResponse,
    summary="Файл yandex_63e4078520e2fe9d.html",
    include_in_schema=False,
    tags=["Веб-сайт"],
)
async def get_yandex_file(request: Request) -> FileResponse:
    """
    Отдаёт yandex_63e4078520e2fe9d.html
    :param request: Request Object
    :return: FileResponse Object
    """
    return FileResponse(
        path=STATIC_DIR / "yandex_63e4078520e2fe9d.html"
    )


@app.post(
    '/application',
    response_class=RedirectResponse,
    summary='Онлайн запись',
    include_in_schema=False,
    tags=["Веб-сайт"]
)
async def application(
    request: Request,
    name: str = Form(None),
    phone: str = Form(None),
) -> RedirectResponse:
    """
    Онлайн запись
    :param name: Name from form
    :param phone: Phone from form
    :param request: Request Object
    :return: RedirectResponse Object
    """

    # Безопасная обработка None и пустых значений
    name = name.strip() if name else '—'
    phone = phone.strip() if phone else '—'

    subject = f"Онлайн запись"
    body = f"""
                <p>Здравствуйте, Кирилл Александрович!</p>
                <p>У вас новая онлайн запись с сайта Los—IT</p>
                <p>Данные из заявки:</p>
                <ul>
                    <li><b>Имя:</b> {name}</li>
                    <li><b>Телефон:</b> {phone}</li>
                </ul>
                """
    await send_email('udarnik.kirill@mail.ru', subject, body)

    return RedirectResponse(
        url='/success',
        status_code=302,
    )