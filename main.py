import json
import asyncio
import datetime
from aiohttp import web


class AdsStorage:

    def __init__(self):
        self._data = {}
        self._next_id = 1
        self._lock = asyncio.Lock()

    async def get_all(self):
        async with self._lock:
            return list(self._data.values())

    async def get_by_id(self, ad_id):
        async with self._lock:
            return self._data.get(ad_id)

    async def create(self, data):
        async with self._lock:
            ad = {
                "id": self._next_id,
                "title": data["title"],
                "description": data["description"],
                "owner": data["owner"],
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            self._data[self._next_id] = ad
            self._next_id += 1
            return ad

    async def update(self, ad_id, data):
        async with self._lock:
            if ad_id not in self._data:
                return None
            self._data[ad_id].update(data)
            return self._data[ad_id]

    async def delete(self, ad_id):
        async with self._lock:
            if ad_id not in self._data:
                return False
            del self._data[ad_id]
            return True


storage = AdsStorage()


def validate_ad_data(data, required_fields=None):
    if required_fields is None:
        required_fields = ["title", "description", "owner"]

    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"

    for field in ["title", "description", "owner"]:
        if field in data:
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

    is_valid, error_msg = validate_ad_data(data, required_fields=["title", "description", "owner"])
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

    is_valid, error_msg = validate_ad_data(data, required_fields=[])
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


def init_app() -> web.Application:
    app = web.Application()

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