from fastapi import FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import List, Optional

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///cargo_storage.db"
engine = create_engine(DATABASE_URL, echo=True)

# Cargo Model
class Cargo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None  # Added for more details
    category: Optional[str] = None  # Example: "Electronics", "Furniture", etc.
    weight: float  # In kg
    volume: float  # In cubic meters
    fragile: bool = False  # Is the cargo fragile?

# Initialize database and seed sample data
def init_db():
    SQLModel.metadata.create_all(engine)
    seed_data()

def seed_data():
    """Seed the database with initial cargo data if empty."""
    with Session(engine) as session:
        # Check if data already exists
        existing_data = session.exec(select(Cargo)).first()
        if not existing_data:
            sample_products = [
                Cargo(name="Laptop", description="Dell Inspiron 15 with Intel i7 processor",
                      category="Electronics", weight=2.5, volume=0.01, fragile=True),
                Cargo(name="Books", description="10 Science books",
                      category="Education", weight=5.0, volume=0.02, fragile=False)
            ]
            session.add_all(sample_products)
            session.commit()

@app.on_event("startup")
def on_startup():
    init_db()

# Add Cargo
@app.post("/cargo", response_model=Cargo)
def add_cargo(cargo: Cargo):
    """Add a new cargo item to storage."""
    with Session(engine) as session:
        session.add(cargo)
        session.commit()
        session.refresh(cargo)
    return cargo

# Get Cargo by ID
@app.get("/cargo/{cargo_id}", response_model=Cargo)
def get_cargo(cargo_id: int):
    """Retrieve a specific cargo item by ID."""
    with Session(engine) as session:
        cargo = session.get(Cargo, cargo_id)
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo not found")
        return cargo

# List all Cargo
@app.get("/cargo", response_model=List[Cargo])
def list_cargo():
    """List all stored cargo items."""
    with Session(engine) as session:
        return session.exec(select(Cargo)).all()

# Update Cargo (Supports Partial Updates)
@app.put("/cargo/{cargo_id}", response_model=Cargo)
def update_cargo(cargo_id: int, updated_cargo: Cargo):
    """Update details of a stored cargo item."""
    with Session(engine) as session:
        cargo = session.get(Cargo, cargo_id)
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo not found")
        
        cargo_data = updated_cargo.dict(exclude_unset=True)
        for key, value in cargo_data.items():
            setattr(cargo, key, value)
        
        session.commit()
        session.refresh(cargo)
    return cargo

# Delete Cargo
@app.delete("/cargo/{cargo_id}", response_model=dict)
def delete_cargo(cargo_id: int):
    """Delete a cargo item from storage."""
    with Session(engine) as session:
        cargo = session.get(Cargo, cargo_id)
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo not found")
        session.delete(cargo)
        session.commit()
    return {"message": "Cargo deleted successfully"}

# Optimize Storage
@app.get("/cargo/optimize")
def optimize_storage(
    max_weight: float = Query(..., description="Maximum weight capacity"),
    max_volume: float = Query(..., description="Maximum volume capacity")
):
    """Optimize storage by selecting cargo that fits within given weight and volume constraints."""
    with Session(engine) as session:
        all_cargo = session.exec(select(Cargo)).all()
        optimized_cargo = []
        total_weight = 0
        total_volume = 0

        for cargo in sorted(all_cargo, key=lambda x: (x.weight, x.volume)):
            if total_weight + cargo.weight <= max_weight and total_volume + cargo.volume <= max_volume:
                optimized_cargo.append(cargo)
                total_weight += cargo.weight
                total_volume += cargo.volume

    return {
        "optimized_cargo": [{"id": c.id, "name": c.name, "weight": c.weight, "volume": c.volume} for c in optimized_cargo],
        "total_weight": total_weight,
        "total_volume": total_volume
    }

# Global inventory dictionary to store item details
inventory = {}

# Add Item
@app.post("/inventory")
def add_item(
    item_id: str,
    name: str,
    category: str,
    location: str,
    width: float,
    height: float,
    depth: float,
    mass: float,
    usage_limit: int
):
    """Add a new item to the inventory."""
    if item_id in inventory:
        raise HTTPException(status_code=400, detail="Item ID already exists.")
    
    # Calculate volume
    volume = width * height * depth if height > 0 else width * depth
    
    # Simulate sensor status
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
    return {"message": f"Item '{name}' added successfully."}

# Use Item
@app.put("/inventory/use/{item_id}")
def use_item(item_id: str):
    """Use an item from the inventory."""
    if item_id not in inventory:
        raise HTTPException(status_code=404, detail="Item not found.")
    
    item = inventory[item_id]
    if item["remaining_uses"] > 0:
        item["remaining_uses"] -= 1
        alert = None
        if item["remaining_uses"] <= 0.1 * item["usage_limit"]:
            alert = f"Alert: '{item['name']}' is nearing its usage limit."
        return {
            "message": f"Used '{item['name']}'. Remaining uses: {item['remaining_uses']}",
            "alert": alert
        }
    else:
        raise HTTPException(status_code=400, detail=f"Item '{item['name']}' has reached its usage limit.")

# Check Storage Status
@app.get("/inventory/status")
def check_storage():
    """Check the total storage status."""
    total_volume = sum(item["volume"] for item in inventory.values())
    total_mass = sum(item["mass"] for item in inventory.values())
    return {
        "total_volume": total_volume,
        "total_mass": total_mass
    }

# View Inventory Items
@app.get("/inventory")
def view_items():
    """View all items in the inventory."""
    if not inventory:
        return {"message": "No items in the inventory."}
    return inventory

# Optimize Storage
@app.get("/inventory/optimize")
def optimize_storage():
    """Provide storage optimization suggestions."""
    if not inventory:
        return {"message": "No items to optimize."}
    
    # Group items by category
    categories = {}
    for item in inventory.values():
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item["name"])
    
    return {
        "suggestions": [
            {"category": cat, "items": items} for cat, items in categories.items()
        ],
        "note": "Place high-usage items in easily accessible locations for efficiency."
    }

# Run the FastAPI App
from typing import List, Dict, Any

def format_response(optimized_cargo: List[Any], total_weight: float, total_volume: float) -> Dict[str, Any]:
    return {
        "optimized_cargo": [{"id": c.id, "name": c.name, "weight": c.weight, "volume": c.volume} for c in optimized_cargo],
        "total_weight": total_weight,
        "total_volume": total_volume
    }

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Run the FastAPI App
if __name__ == "__main__":
    import uvicorn
    import os

    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", 8000))

    try:
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        print(f"Error starting the server: {e}")