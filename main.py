import json
import datetime
import aiosqlite
from aiohttp import web

DB_PATH = "ads.db"


class AdsStorage:

    def __init__(self, db_path):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            await db.commit()

    async def get_all(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM ads")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_by_id(self, ad_id):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM ads WHERE id = ?", (ad_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def create(self, data):
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO ads (title, description, owner, created_at) VALUES (?, ?, ?, ?)",
                (data["title"], data["description"], data["owner"], created_at)
            )
            await db.commit()
            return {
                "id": cursor.lastrowid,
                "title": data["title"],
                "description": data["description"],
                "owner": data["owner"],
                "created_at": created_at
            }

    async def update(self, ad_id, data):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE ads SET title = ?, description = ?, owner = ? WHERE id = ?",
                (data["title"], data["description"], data["owner"], ad_id)
            )
            await db.commit()
        return await self.get_by_id(ad_id)

    async def delete(self, ad_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM ads WHERE id = ?", (ad_id,))
            await db.commit()
            return cursor.rowcount > 0


storage = AdsStorage(DB_PATH)


def validate_ad_data(data):
    required_fields = ["title", "description", "owner"]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        if not isinstance(data[field], str) or not data[field].strip():
            return False, f"Field '{field}' must be a non-empty string"

    return True, None


async def get_ads(request: web.Request) -> web.Response:
    ads = await storage.get_all()
    return web.json_response(ads)


async def get_ad(request: web.Request) -> web.Response:
    try:
        ad_id = int(request.match_info['id'])
    except ValueError:
        return web.json_response({"error": "Invalid ID"}, status=400)

    ad = await storage.get_by_id(ad_id)
    if not ad:
        return web.json_response({"error": "Ad not found"}, status=404)

    return web.json_response(ad)


async def create_ad(request: web.Request) -> web.Response:
    try:
        body = await request.text()
        data = json.loads(body)
    except json.JSONDecodeError as e:
        return web.json_response({"error": f"Invalid JSON: {str(e)}"}, status=400)

    is_valid, error_msg = validate_ad_data(data)
    if not is_valid:
        return web.json_response({"error": error_msg}, status=400)

    ad = await storage.create(data)
    return web.json_response(ad, status=201)


async def update_ad(request: web.Request) -> web.Response:
    try:
        ad_id = int(request.match_info['id'])
    except ValueError:
        return web.json_response({"error": "Invalid ID"}, status=400)

    existing = await storage.get_by_id(ad_id)
    if not existing:
        return web.json_response({"error": "Ad not found"}, status=404)

    try:
        body = await request.text()
        data = json.loads(body)
    except json.JSONDecodeError as e:
        return web.json_response({"error": f"Invalid JSON: {str(e)}"}, status=400)

    is_valid, error_msg = validate_ad_data(data)
    if not is_valid:
        return web.json_response({"error": error_msg}, status=400)

    ad = await storage.update(ad_id, data)
    return web.json_response(ad)


async def delete_ad(request: web.Request) -> web.Response:
    try:
        ad_id = int(request.match_info['id'])
    except ValueError:
        return web.json_response({"error": "Invalid ID"}, status=400)

    deleted = await storage.delete(ad_id)
    if not deleted:
        return web.json_response({"error": "Ad not found"}, status=404)

    return web.json_response({"status": "deleted"})


async def on_startup(app):
    await storage.init_db()
    print("База данных инициализирована")


def init_app() -> web.Application:
    app = web.Application()

    app.on_startup.append(on_startup)

    app.router.add_get('/ads', get_ads)
    app.router.add_get('/ads/{id}', get_ad)
    app.router.add_post('/ads', create_ad)
    app.router.add_put('/ads/{id}', update_ad)
    app.router.add_delete('/ads/{id}', delete_ad)

    return app


if __name__ == '__main__':
    app = init_app()
    print("Сервер запущен на http://127.0.0.1:5000")
    web.run_app(app, host='127.0.0.1', port=5000)