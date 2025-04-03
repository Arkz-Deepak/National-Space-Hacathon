from flask import Flask, request, jsonify

app = Flask(__name__)

# Global inventory dictionary to store item details
inventory = {}

@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.json
    item_id = data.get("item_id")
    if item_id in inventory:
        return jsonify({"error": "Item ID already exists. Please use a unique ID."}), 400
    
    try:
        name = data["name"]
        category = data["category"]
        location = data["location"]
        width = float(data["width"])
        height = float(data["height"])
        depth = float(data["depth"])
        mass = float(data["mass"])
        usage_limit = int(data["usage_limit"])
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except ValueError:
        return jsonify({"error": "Invalid input for dimensions, mass, or usage limit."}), 400

    volume = width * height * depth if height > 0 else width * depth
    sensor_status = "Nominal"

    inventory[item_id] = {
        "name": name,
        "category": category,
        "location": location,
        "width": width,
        "height": height,
        "depth": depth,
        "mass": mass,
        "usage_limit": usage_limit,
        "remaining_uses": usage_limit,
        "volume": volume,
        "sensor_status": sensor_status
    }
    return jsonify({"message": f"Item '{name}' added successfully."}), 201

@app.route('/use_item/<item_id>', methods=['PUT'])
def use_item(item_id):
    if item_id not in inventory:
        return jsonify({"error": "Item not found."}), 404
    
    item = inventory[item_id]
    if item["remaining_uses"] > 0:
        item["remaining_uses"] -= 1
        alert = None
        if 0 < item["remaining_uses"] <= 0.1 * item["usage_limit"]:  # Fix condition
            alert = f"Alert: '{item['name']}' is nearing its usage limit. Consider reordering or maintenance."
        return jsonify({
            "message": f"Used '{item['name']}'. Remaining uses: {item['remaining_uses']}",
            "alert": alert
        }), 200
    else:
        return jsonify({"error": f"Item '{item['name']}' has reached its usage limit. Replacement is required."}), 400

@app.route('/check_storage', methods=['GET'])
def check_storage():
    total_volume = sum(item["volume"] for item in inventory.values())
    total_mass = sum(item["mass"] for item in inventory.values())
    return jsonify({
        "total_volume": total_volume,
        "total_mass": total_mass
    }), 200

@app.route('/view_items', methods=['GET'])
def view_items():
    if not inventory:
        return jsonify({"message": "No items in the inventory."}), 200
    return jsonify(inventory), 200

@app.route('/optimize_storage', methods=['GET'])
def optimize_storage():
    if not inventory:
        return jsonify({"message": "No items to optimize."}), 200
    
    categories = {}
    for item in inventory.values():
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item["name"])
    
    return jsonify({
        "suggestions": {
            "group_by_category": categories,
            "note": "Place high-usage items in easily accessible locations for efficiency."
        }
    }), 200

if __name__ == '__main__':
    app.run(debug=True)