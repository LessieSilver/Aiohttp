from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

ads = {}
current_id = 1

@app.route('/ads', methods=['POST'])
def create_ad():
    global current_id
    data = request.get_json()

    if not data or not all(k in data for k in ('title', 'description', 'owner')):
        return jsonify({'error': 'Missing required fields: title, description, owner'}), 400

    new_ad = {
        'id': current_id,
        'title': data['title'],
        'description': data['description'],
        'owner': data['owner'],
        'created_at': datetime.now().isoformat()
    }

    ads[current_id] = new_ad
    current_id += 1

    return jsonify(new_ad), 201

@app.route('/ads/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    ad = ads.get(ad_id)
    if not ad:
        return jsonify({'error': 'Ad not found'}), 404
    return jsonify(ad), 200

@app.route('/ads', methods=['GET'])
def get_all_ads():
    return jsonify(list(ads.values())), 200

@app.route('/ads/<int:ad_id>', methods=['PUT'])
def update_ad(ad_id):
    ad = ads.get(ad_id)
    if not ad:
        return jsonify({'error': 'Ad not found'}), 404

    data = request.get_json()

    ad['title'] = data.get('title', ad['title'])
    ad['description'] = data.get('description', ad['description'])
    ad['owner'] = data.get('owner', ad['owner'])

    return jsonify(ad), 200

@app.route('/ads/<int:ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    deleted_ad = ads.pop(ad_id, None)

    if not deleted_ad:
        return jsonify({'error': 'Ad not found'}), 404

    return jsonify({'message': 'Ad successfully deleted'}), 200


if __name__ == '__main__':
    app.run(debug=True)