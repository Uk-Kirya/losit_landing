import json
import sqlite3
import logging

from pathlib import Path
from datetime import datetime, date, timedelta, timezone
from threading import Lock

from user_agents import parse


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "analytics.db"
LOG_PATH = DATA_DIR / "visits.jsonl"
GEOIP_PATH = BASE_DIR / "GeoLite2-City.mmdb"

SESSION_MINUTES = 30
DB_LOCK = Lock()

logger = logging.getLogger("visits")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

geo_reader = None

try:
    import geoip2.database
    if GEOIP_PATH.exists():
        geo_reader = geoip2.database.Reader(str(GEOIP_PATH))
except Exception:
    geo_reader = None


def now_utc():
    return datetime.now(timezone.utc)


def timestamp():
    return now_utc().isoformat(timespec="seconds")


def connect():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with DB_LOCK, connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visited_at TEXT NOT NULL,
                path TEXT NOT NULL,
                method TEXT NOT NULL,
                device TEXT NOT NULL,
                country TEXT NOT NULL,
                city TEXT NOT NULL,
                session_id TEXT NOT NULL,
                client_ip TEXT
            );

            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_visits_date
            ON visits(visited_at);

            CREATE INDEX IF NOT EXISTS idx_visits_path
            ON visits(path);
        """)


def get_location(ip: str):
    if not geo_reader or not ip:
        return "Не определено", "Не определён"

    try:
        result = geo_reader.city(ip)
        country = result.country.name or "Не определено"
        city = result.city.name or "Не определён"
        return country, city
    except Exception:
        return "Не определено", "Не определён"


def get_device(user_agent: str):
    ua = parse(user_agent or "")

    if ua.is_tablet:
        return "Планшет"
    if ua.is_mobile:
        return "Телефон"
    if ua.is_pc:
        return "Компьютер"

    return "Не определено"


def register_visit(
    session_id: str,
    path: str,
    method: str,
    user_agent: str,
    ip: str,
):
    now = now_utc()
    current_time = now.isoformat(timespec="seconds")
    cutoff = (now - timedelta(minutes=SESSION_MINUTES)).isoformat(
        timespec="seconds"
    )

    country, city = get_location(ip)
    device = get_device(user_agent)

    with DB_LOCK, connect() as conn:
        session = conn.execute(
            "SELECT last_seen FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()

        # Если активности не было более 30 минут — новая сессия.
        if session and session["last_seen"] < cutoff:
            import uuid
            session_id = str(uuid.uuid4())
            session = None

        if session is None:
            conn.execute(
                """
                INSERT INTO sessions (session_id, first_seen, last_seen)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    last_seen = excluded.last_seen
                """,
                (session_id, current_time, current_time),
            )
        else:
            conn.execute(
                "UPDATE sessions SET last_seen = ? WHERE session_id = ?",
                (current_time, session_id),
            )

        conn.execute(
            """
            INSERT INTO visits (
                visited_at, path, method, device,
                country, city, session_id, client_ip
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                current_time, path, method, device,
                country, city, session_id, ip,
            ),
        )

    event = {
        "visited_at": current_time,
        "path": path,
        "method": method,
        "device": device,
        "country": country,
        "city": city,
        "session_id": session_id,
        "ip": ip,
    }

    logger.info(json.dumps(event, ensure_ascii=False))

    return session_id



def get_stats(
    start_date: date | None = None,
    end_date: date | None = None,
    all_time: bool = False,
):
    from zoneinfo import ZoneInfo

    moscow_tz = ZoneInfo("Europe/Moscow")

    # Границы периода в UTC
    start_utc = None
    end_utc = None

    if not all_time and start_date and end_date:
        start_utc = datetime.combine(
            start_date,
            datetime.min.time(),
            tzinfo=moscow_tz,
        ).astimezone(timezone.utc)

        end_utc = datetime.combine(
            end_date + timedelta(days=1),
            datetime.min.time(),
            tzinfo=moscow_tz,
        ).astimezone(timezone.utc)

    where = ""
    params = []

    if start_utc and end_utc:
        where = "WHERE visited_at >= ? AND visited_at < ?"
        params = [
            start_utc.isoformat(),
            end_utc.isoformat(),
        ]

    with DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        try:
            # Всего уникальных сессий за всю историю
            total_unique = conn.execute("""
                SELECT COUNT(DISTINCT session_id)
                FROM visits
            """).fetchone()[0]

            # Уникальные сессии за сегодня по московскому времени
            today = datetime.now(moscow_tz).date()

            today_start = datetime.combine(
                today,
                datetime.min.time(),
                tzinfo=moscow_tz,
            ).astimezone(timezone.utc)

            tomorrow_start = datetime.combine(
                today + timedelta(days=1),
                datetime.min.time(),
                tzinfo=moscow_tz,
            ).astimezone(timezone.utc)

            today_unique = conn.execute("""
                SELECT COUNT(DISTINCT session_id)
                FROM visits
                WHERE visited_at >= ? AND visited_at < ?
            """, (
                today_start.isoformat(),
                tomorrow_start.isoformat(),
            )).fetchone()[0]

            # Активные сессии за последние 30 минут
            active_since = (
                datetime.now(timezone.utc) - timedelta(minutes=30)
            ).isoformat()

            active = conn.execute("""
                SELECT COUNT(*)
                FROM sessions
                WHERE last_seen >= ?
            """, (active_since,)).fetchone()[0]

            # Посещения за выбранный период
            rows = conn.execute(f"""
                SELECT
                    visited_at,
                    path,
                    method,
                    device,
                    country,
                    city,
                    session_id,
                    client_ip
                FROM visits
                {where}
                ORDER BY visited_at DESC
            """, params).fetchall()

            # Группировка посещений по сессиям
            sessions_dict = {}

            for row in rows:
                sid = row["session_id"]

                if sid not in sessions_dict:
                    sessions_dict[sid] = {
                        "session_id": sid,
                        "first_seen": row["visited_at"],
                        "last_seen": row["visited_at"],
                        "page_count": 0,
                        "device": row["device"],
                        "country": row["country"],
                        "city": row["city"],
                        "client_ip": row["client_ip"],
                        "pages": [],
                    }

                session = sessions_dict[sid]
                session["page_count"] += 1
                session["first_seen"] = min(
                    session["first_seen"],
                    row["visited_at"],
                )
                session["last_seen"] = max(
                    session["last_seen"],
                    row["visited_at"],
                )
                session["pages"].append({
                    "visited_at": row["visited_at"],
                    "path": row["path"],
                    "method": row["method"],
                })

            sessions_list = sorted(
                sessions_dict.values(),
                key=lambda s: s["last_seen"],
                reverse=True,
            )

            # Популярные страницы за выбранный период
            pages = conn.execute(f"""
                SELECT path, COUNT(*) AS views
                FROM visits
                {where}
                GROUP BY path
                ORDER BY views DESC
                LIMIT 10
            """, params).fetchall()

            # Устройства за выбранный период
            devices = conn.execute(f"""
                SELECT device, COUNT(*) AS count
                FROM visits
                {where}
                GROUP BY device
                ORDER BY count DESC
            """, params).fetchall()

            return {
                "total_unique": total_unique,
                "today_unique": today_unique,
                "filtered_unique": len(sessions_list),
                "active": active,
                "sessions": sessions_list,
                "pages": [
                    {"path": row["path"], "views": row["views"]}
                    for row in pages
                ],
                "devices": [
                    {"device": row["device"], "count": row["count"]}
                    for row in devices
                ],
                "start_date": start_date.isoformat() if start_date else "",
                "end_date": end_date.isoformat() if end_date else "",
                "all_time": all_time,
            }

        finally:
            conn.close()

init_db()
