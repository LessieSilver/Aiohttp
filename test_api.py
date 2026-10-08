import urllib.request
import json

BASE_URL = "http://127.0.0.1:5000/ads"

print("1. Проверяем GET (список объявлений должен быть пустым):")
with urllib.request.urlopen(BASE_URL) as response:
    print(response.read().decode('utf-8'))

print("\n2. Создаем объявление (POST):")
data = json.dumps({
    "title": "Продам велосипед",
    "description": "Новый, горный, черный",
    "owner": "Иван Иванов"
}).encode('utf-8')

req = urllib.request.Request(BASE_URL, data=data, headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode('utf-8'))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    ad_id = result['id']

print(f"\n3. Получаем созданное объявление по ID {ad_id} (GET):")
with urllib.request.urlopen(f"{BASE_URL}/{ad_id}") as response:
    print(response.read().decode('utf-8'))

print(f"\n4. Редактируем объявление {ad_id} (PUT):")
update_data = json.dumps({
    "title": "Продам горный велосипед (скидка!)",
    "description": "Новый, горный, черный",
    "owner": "Иван Иванов"
}).encode('utf-8')
req_put = urllib.request.Request(f"{BASE_URL}/{ad_id}", data=update_data, headers={'Content-Type': 'application/json'}, method='PUT')
with urllib.request.urlopen(req_put) as response:
    print(response.read().decode('utf-8'))

print(f"\n5. Удаляем объявление {ad_id} (DELETE):")
req_delete = urllib.request.Request(f"{BASE_URL}/{ad_id}", method='DELETE')
with urllib.request.urlopen(req_delete) as response:
    print(response.read().decode('utf-8'))

print("\n6. Снова проверяем список (должен быть пустым):")
with urllib.request.urlopen(BASE_URL) as response:
    print(response.read().decode('utf-8'))