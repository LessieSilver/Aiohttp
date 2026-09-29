import json
from aiohttp import web

ads_db = {}
next_id = 1


async def get_ads(request: web.Request) -> web.Response:
    return web.json_response(list(ads_db.values()))


async def get_ad(request: web.Request) -> web.Response:
    try:
        ad_id = int(request.match_info['id'])
    except ValueError:
        return web.json_response({"error": "Invalid ID"}, status=400)

    if ad_id not in ads_db:
        return web.json_response({"error": "Ad not found"}, status=404)

    return web.json_response(ads_db[ad_id])


async def create_ad(request: web.Request) -> web.Response:
    global next_id

    try:
        body = await request.text()
        data = json.loads(body)
    except json.JSONDecodeError as e:
        return web.json_response({"error": f"Invalid JSON: {str(e)}"}, status=400)
    except Exception as e:
        return web.json_response({"error": f"Error: {str(e)}"}, status=400)

    required_fields = ["title", "description", "owner"]
    for field in required_fields:
        if field not in data:
            return web.json_response({"error": f"Missing field: {field}"}, status=400)

    ad = {
        "id": next_id,
        "title": data["title"],
        "description": data["description"],
        "owner": data["owner"]
    }

    ads_db[next_id] = ad
    next_id += 1

    return web.json_response(ad, status=201)


async def update_ad(request: web.Request) -> web.Response:
    try:
        ad_id = int(request.match_info['id'])
    except ValueError:
        return web.json_response({"error": "Invalid ID"}, status=400)

    if ad_id not in ads_db:
        return web.json_response({"error": "Ad not found"}, status=404)

    try:
        body = await request.text()
        data = json.loads(body)
    except json.JSONDecodeError as e:
        return web.json_response({"error": f"Invalid JSON: {str(e)}"}, status=400)
    except Exception as e:
        return web.json_response({"error": f"Error: {str(e)}"}, status=400)

    ads_db[ad_id].update(data)
    return web.json_response(ads_db[ad_id])


async def delete_ad(request: web.Request) -> web.Response:
    try:
        ad_id = int(request.match_info['id'])
    except ValueError:
        return web.json_response({"error": "Invalid ID"}, status=400)

    if ad_id not in ads_db:
        return web.json_response({"error": "Ad not found"}, status=404)

    del ads_db[ad_id]
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