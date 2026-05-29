from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import schemas, crud
from .models import Base
from datetime import datetime
from .database import engine, get_db

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.post("/items/", response_model=schemas.UserResponse)
def create_item(User: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=User)

@app.post("/match/{user1_id}/{user2_id}")
def match(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
    try:
        return crud.simulate_match(db, user1_id, user2_id)
    except ValueError as e:
        return {'error': str(e)}

@app.get("/items/{item_id}", response_model=schemas.UserResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_item

@app.get("/items/", response_model=list[schemas.UserResponse])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/health/")
def get_health():
    return {
        'status': 'ok',
        'time': datetime.now().isoformat()
        }