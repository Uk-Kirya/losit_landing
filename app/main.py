from pathlib import Path

from fastapi import FastAPI, Request, Form, Depends
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

from app.recaptcha_check import recaptcha_check
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
            "status_code": exc.status_code,
            "detail": exc.detail
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
    '/cookies',
    response_class=HTMLResponse,
    summary='Страница с политикой cookies',
    include_in_schema=False,
    name='cookies',
    tags=["Веб-сайт"]
)
async def get_cookies(
    request: Request
) -> HTMLResponse:
    """
    Страница политика cookies
    :param request: Request Object
    :return: HTMLResponse Object
    """

    return templates.TemplateResponse(
        'cookies.html',
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
    '/anketa',
    response_class=HTMLResponse,
    summary='Анкета ученика',
    include_in_schema=False,
    name='questionnaire',
    tags=["Веб-сайт"]
)
async def questionnaire(
    request: Request
) -> HTMLResponse:
    """
    Анкета ученика
    :param request: Request Object
    :return: HTMLResponse Object
    """

    return templates.TemplateResponse(
        'questionnaire.html',
        {
            'request': request,
        }
    )


@app.get(
    '/success-questionnaire',
    response_class=HTMLResponse,
    summary='Анкета отправлена',
    include_in_schema=False,
    tags=["Веб-сайт"]
)
async def success_questionnaire(
    request: Request
) -> HTMLResponse:
    """
    Анкета отправлена
    :param request: Request Object
    :return: HTMLResponse Object
    """

    return templates.TemplateResponse(
        'success-questionnaire.html',
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
    name: str = Form(default=None, description='Имя'),
    phone: str = Form(default=None, description='Телефон'),
    google_recaptcha_check: None = Depends(recaptcha_check),
) -> RedirectResponse:
    """
    Онлайн запись
    :param name: Name from form
    :param phone: Phone from form
    :param request: Request Object
    :param google_recaptcha_check: Check Google reCaptcha from form
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
    await send_email('info@los-it.ru', subject, body)

    return RedirectResponse(
        url='/success',
        status_code=302,
    )


@app.post(
    '/anketa',
    response_class=RedirectResponse,
    summary='Онлайн запись',
    name='questionnaire_application',
    include_in_schema=False,
    tags=["Веб-сайт"]
)
async def questionnaire_application(
    request: Request,

    parent_name: str = Form(None),
    parent_phone: str = Form(None),
    parent_email: str = Form(None),
    messanger_max: str = Form(None),
    messanger_whatsapp: str = Form(None),
    messanger_telegram: str = Form(None),

    child_name: str = Form(None),
    child_female: str = Form(None),
    child_age: str = Form(None),
    child_bio: str = Form(None),
) -> RedirectResponse:
    """
    Онлайн запись
    :param parent_name: Parent Name from form
    :param parent_phone: Parent Phone from form
    :param parent_email: Parent E-mail from form
    :param messanger_max: MAX from form
    :param messanger_whatsapp: WhatsApp from form
    :param messanger_telegram: Telegram from form
    :param child_name: Child Name from form
    :param child_female: Child Female from form
    :param child_age: Child Age from form
    :param child_bio: Child Biography from form
    :return: RedirectResponse Object
    """

    # Безопасная обработка None и пустых значений
    parent_name = parent_name.strip() if parent_name else '—'
    parent_phone = parent_phone.strip() if parent_phone else '—'
    parent_email = parent_email.strip() if parent_email else '—'
    messanger_max = messanger_max.strip() if messanger_max else '—'
    messanger_whatsapp = messanger_whatsapp.strip() if messanger_whatsapp else '—'
    messanger_telegram = messanger_telegram.strip() if messanger_telegram else '—'
    child_name = child_name.strip() if child_name else '—'
    child_female = child_female.strip() if child_female else '—'
    child_age = child_age.strip() if child_age else '—'
    child_bio = child_bio.strip() if child_bio else '—'

    subject = f"Анкета ученика"
    body = f"""
                <p>Здравствуйте, Кирилл Александрович!</p>
                <p>У вас новые данные ученика с сайта Los—IT</p>
                <p>Данные из анкеты:</p>
                <i>Родитель</i>
                <ul>
                    <li><b>Имя родителя:</b> {parent_name}</li>
                    <li><b>Телефон родителя:</b> {parent_phone}</li>
                    <li><b>E-mail родителя:</b> {parent_email}</li>
                    <li><b>MAX:</b> {messanger_max}</li>
                    <li><b>WhatsApp:</b> {messanger_whatsapp}</li>
                    <li><b>Telegram:</b> {messanger_telegram}</li>
                </ul>
                <i>Ребенок</i>
                <ul>
                    <li><b>Имя:</b> {child_name}</li>
                    <li><b>Пол:</b> {child_female}</li>
                    <li><b>Возраст:</b> {child_age}</li>
                    <li><b>Биография:</b> {child_bio}</li>
                </ul>
                """
    await send_email('info@los-it.ru', subject, body)

    return RedirectResponse(
        url='/success-questionnaire',
        status_code=302,
    )