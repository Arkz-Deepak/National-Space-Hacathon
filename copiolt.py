from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List

app = FastAPI()

# In-memory storage for demonstration purposes
storage: Dict[str, Dict] = {}

class StorageItem(BaseModel):
    id: str
    name: str
    value: str

class UpdateStorageItem(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None

@app.post('/storage', response_model=Dict[str, str])
def create_storage(item: StorageItem):
    if item.id in storage:
        raise HTTPException(status_code=400, detail="Storage already exists")
    storage[item.id] = item.dict()
    return {"message": "Storage created successfully"}

@app.get('/storage/{storage_id}', response_model=Dict)
def retrieve_storage(storage_id: str):
    if storage_id not in storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    return storage[storage_id]

@app.put('/storage/{storage_id}', response_model=Dict[str, str])
def update_storage(storage_id: str, item: UpdateStorageItem):
    if storage_id not in storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    if item.name is not None:
        storage[storage_id]['name'] = item.name
    if item.value is not None:
        storage[storage_id]['value'] = item.value
    return {"message": "Storage updated successfully"}

@app.delete('/storage/{storage_id}', response_model=Dict[str, str])
def delete_storage(storage_id: str):
    if storage_id not in storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    del storage[storage_id]
    return {"message": "Storage deleted successfully"}

@app.get('/storage', response_model=List[Dict])
def list_storage():
    return list(storage.values())

@app.get('/storage/search', response_model=List[Dict])
def search_storage(name: Optional[str] = None, value: Optional[str] = None):
    results = []
    for item in storage.values():
        if name and item['name'] == name:
            results.append(item)
        elif value and item['value'] == value:
            results.append(item)
    return results

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)