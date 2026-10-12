from datetime import datetime, date, timedelta
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import (
    RedirectResponse,
    FileResponse,
    HTMLResponse,
    StreamingResponse,
)

from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from zoneinfo import ZoneInfo

from app.CounterMiddleware import CounterMiddleWare
from app.mailer import send_email
from app.analytics import get_stats

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CounterMiddleWare
)

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



from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo


def resolve_analytics_filter(
    period: str = "today",
    start_date: date | None = None,
    end_date: date | None = None,
    selected_date: date | None = None,
):
    today = datetime.now(ZoneInfo("Europe/Moscow")).date()

    # Конкретная дата
    if selected_date:
        return selected_date, selected_date, False, "date"

    # Произвольный диапазон дат
    if start_date or end_date:
        start = start_date or end_date or today
        end = end_date or start_date or today

        # Если даты введены в обратном порядке — меняем их местами
        if start > end:
            start, end = end, start

        return start, end, False, "custom"

    # Вся история
    if period == "all":
        return None, None, True, "all"

    # Последние 1, 3 или 7 календарных дней
    if period in ("1", "3", "7"):
        days = int(period)
        return today - timedelta(days=days - 1), today, False, period

    # По умолчанию — сегодня
    return today, today, False, "today"

@app.get(
    "/analytics",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def analytics_page(
    request: Request,
    period: str = Query(default="today"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    date: date | None = Query(default=None),
):
    start, end, all_time, selected_period = resolve_analytics_filter(
        period=period,
        start_date=start_date,
        end_date=end_date,
        selected_date=date,
    )

    stats = get_stats(
        start_date=start,
        end_date=end,
        all_time=all_time,
    )

    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "stats": stats,
            "period": selected_period,
            "start_date": start.isoformat() if start else "",
            "end_date": end.isoformat() if end else "",
            "selected_date": date.isoformat() if date else "",
        },
    )


@app.get(
    "/analytics/export.xlsx",
    include_in_schema=False,
)
async def export_analytics(
    period: str = Query(default="today"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    date: date | None = Query(default=None),
):
    start, end, all_time, selected_period = resolve_analytics_filter(
        period=period,
        start_date=start_date,
        end_date=end_date,
        selected_date=date,
    )

    stats = get_stats(
        start_date=start,
        end_date=end,
        all_time=all_time,
    )

    workbook = Workbook()

    # Лист 1: сводка.
    summary = workbook.active
    summary.title = "Сводка"
    summary.append(["Показатель", "Значение"])
    summary.append(["Уникальные посещения за всё время", stats["total_unique"]])
    summary.append(["Уникальные посещения сегодня", stats["today_unique"]])
    summary.append(["Уникальные посещения за выбранный период", stats["filtered_unique"]])
    summary.append(["Активные сессии за последние 30 минут", stats["active"]])
    summary.append([
        "Период",
        "Всё время" if all_time else f"{start} — {end}",
    ])

    # Лист 2: уникальные посещения.
    sessions_sheet = workbook.create_sheet("Посещения")
    sessions_sheet.append([
        "ID сессии",
        "Первое посещение",
        "Последнее посещение",
        "Количество страниц",
        "Устройство",
        "Страна",
        "Город",
        "IP",
    ])

    # Лист 3: каждая посещённая страница.
    pages_sheet = workbook.create_sheet("Страницы")
    pages_sheet.append([
        "ID сессии",
        "Дата и время",
        "URL",
        "Метод",
        "Устройство",
        "Страна",
        "Город",
        "IP",
    ])

    for session in stats["sessions"]:
        sessions_sheet.append([
            session["session_id"],
            session["first_seen"],
            session["last_seen"],
            session["page_count"],
            session["device"],
            session["country"],
            session["city"],
            session["client_ip"] or "",
        ])

        for page in session["pages"]:
            pages_sheet.append([
                session["session_id"],
                page["visited_at"],
                page["path"],
                page["method"],
                session["device"],
                session["country"],
                session["city"],
                session["client_ip"] or "",
            ])

    # Оформление листов.
    for sheet in workbook.worksheets:
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions

        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(
                fill_type="solid",
                fgColor="1E90FF",
            )
            cell.alignment = Alignment(vertical="center")

        for column in sheet.columns:
            column_letter = column[0].column_letter
            max_length = max(
                (len(str(cell.value or "")) for cell in column),
                default=10,
            )
            sheet.column_dimensions[column_letter].width = min(
                max(max_length + 2, 12),
                45,
            )

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    filename = f"los_it_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )
