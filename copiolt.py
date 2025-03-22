from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for demonstration purposes
storage = {}

@app.route('/storage', methods=['POST'])
def create_storage():
    data = request.json
    storage_id = data.get('id')
    if storage_id in storage:
        return jsonify({'message': 'Storage already exists'}), 400
    storage[storage_id] = data
    return jsonify({'message': 'Storage created successfully'}), 201

@app.route('/storage/<storage_id>', methods=['GET'])
def retrieve_storage(storage_id):
    if storage_id not in storage:
        return jsonify({'message': 'Storage not found'}), 404
    return jsonify(storage[storage_id]), 200

@app.route('/storage/<storage_id>', methods=['PUT'])
def update_storage(storage_id):
    if storage_id not in storage:
        return jsonify({'message': 'Storage not found'}), 404
    data = request.json
    storage[storage_id] = data
    return jsonify({'message': 'Storage updated successfully'}), 200

@app.route('/storage/<storage_id>', methods=['DELETE'])
def delete_storage(storage_id):
    if storage_id not in storage:
        return jsonify({'message': 'Storage not found'}), 404
    del storage[storage_id]
    return jsonify({'message': 'Storage deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)