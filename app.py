# Pure Python Space Station Storage & Usage Tracking System
# No external modules are imported.

# Global inventory dictionary to store item details
inventory = {}

def add_item():
    print("\n--- Add New Item ---")
    item_id = input("Enter Item ID: ")
    if item_id in inventory:
        print("Item ID already exists. Please use a unique ID.")
        return
    name = input("Enter Item Name: ")
    category = input("Enter Category (e.g., Food, Tool, Medical, Spare Part): ")
    location = input("Enter Storage Location (e.g., Module A-1): ")
    
    # Input dimensions
    try:
        width = float(input("Enter Width (in cm): "))
        height = float(input("Enter Height (in cm, enter 0 if not applicable): "))
        depth = float(input("Enter Depth (in cm): "))
    except:
        print("Invalid input for dimensions. Aborting item addition.")
        return

    # Input mass and usage limit
    try:
        mass = float(input("Enter Mass (in kg): "))
    except:
        print("Invalid input for mass. Aborting item addition.")
        return
    try:
        usage_limit = int(input("Enter Usage Limit (number of times item can be used): "))
    except:
        print("Invalid input for usage limit. Aborting item addition.")
        return
    
    # Calculate volume:
    # If height is provided (> 0), treat as a box: volume = width * height * depth.
    # If height is 0, treat as a 2D approximation (for items like cylinders): volume = width * depth.
    if height > 0:
        volume = width * height * depth
    else:
        volume = width * depth
    
    # Simulate sensor status (assumed nominal for now)
    sensor_status = "Nominal"
    
    # Save item details into the inventory
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
    print("Item '{}' added successfully.".format(name))

def use_item():
    print("\n--- Use an Item ---")
    item_id = input("Enter Item ID to use: ")
    if item_id not in inventory:
        print("Item not found.")
        return
    item = inventory[item_id]
    if item["remaining_uses"] > 0:
        item["remaining_uses"] -= 1
        print("Used '{}'. Remaining uses: {}".format(item["name"], item["remaining_uses"]))
        # Alert if usage is below 10% of the limit
        if item["remaining_uses"] <= 0.1 * item["usage_limit"]:
            print("Alert: '{}' is nearing its usage limit. Consider reordering or maintenance.".format(item["name"]))
    else:
        print("Item '{}' has reached its usage limit. Replacement is required.".format(item["name"]))

def check_storage():
    print("\n--- Storage Status ---")
    total_volume = 0
    total_mass = 0
    for item in inventory.values():
        total_volume += item["volume"]
        total_mass += item["mass"]
    print("Total Storage Volume Used: {} cm³".format(total_volume))
    print("Total Mass Stored: {} kg".format(total_mass))

def view_items():
    print("\n--- Inventory Items ---")
    if not inventory:
        print("No items in the inventory.")
        return
    for item_id, item in inventory.items():
        print("ID: {} | Name: {} | Category: {} | Location: {} | Volume: {} cm³ | Mass: {} kg | Usage: {}/{} | Sensor: {}"
              .format(item_id, item["name"], item["category"], item["location"],
                      item["volume"], item["mass"], item["remaining_uses"],
                      item["usage_limit"], item["sensor_status"]))

def optimize_storage():
    print("\n--- Storage Optimization Suggestions ---")
    if not inventory:
        print("No items to optimize.")
        return
    # Group items by category
    categories = {}
    for item in inventory.values():
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item["name"])
    
    print("Suggested grouping by category:")
    for cat, items in categories.items():
        print("  Category '{}': {}".format(cat, ", ".join(items)))
    print("Also, place high-usage items in easily accessible locations for efficiency.")

def main_menu():
    while True:
        print("\n=== Space Station Storage & Usage Tracking System ===")
        print("1. Add Item")
        print("2. Use Item")
        print("3. Check Storage Status")
        print("4. View Inventory Items")
        print("5. Optimize Storage")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")
        
        if choice == "1":
            add_item()
        elif choice == "2":
            use_item()
        elif choice == "3":
            check_storage()
        elif choice == "4":
            view_items()
        elif choice == "5":
            optimize_storage()
        elif choice == "6":
            print("Exiting system. Safe travels!")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the main menu loop
main_menu()