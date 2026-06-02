import time
from . import schemas, crud
from .models import Base
from datetime import datetime
from .database import engine, get_db
from app.cache import get_cache, set_cache, delete_cache
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

app = FastAPI()


def wait_for_db(engine):
    for _ in range(30):
        try:
            engine.connect()
            return
        except OperationalError:
            time.sleep(1)
    raise Exception("Database never became ready")


@app.on_event("startup")
def startup():
    wait_for_db(engine)
    Base.metadata.create_all(bind=engine)


@app.post("/users/", response_model=schemas.UserResponse)
async def create_item(user: schemas.UserCreate, db: Session = Depends(get_db)):
    created = crud.create_item(db=db, item=user)
    await delete_cache("users:0:10")
    return created


@app.post("/match/{user1_id}/{user2_id}")
async def match(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
    try:
        simulated = crud.simulate_match(db, user1_id, user2_id)
        await delete_cache(f"user:{user1_id}")
        await delete_cache(f"user:{user2_id}")
        return simulated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{item_id}", response_model=schemas.UserResponse)
async def read_item(item_id: int, db: Session = Depends(get_db)):

    cache_key = f"user:{item_id}"
    # Try to read from cache
    cached = await get_cache(cache_key)
    if cached:
        return schemas.UserResponse.model_validate(cached)

    db_item = crud.get_item(db, id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = schemas.UserResponse.model_validate(db_item).model_dump()

    await set_cache(cache_key, result)
    return result


@app.get("/users/", response_model=list[schemas.UserResponse])
async def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    cache_key = f"users:{skip}:{limit}"
    # Try to read from cache
    cached = await get_cache(cache_key)
    if cached:
        print("CACHE HIT")
        return [schemas.UserResponse.model_validate(i) for i in cached]

    print("CACHE MISS")
    items = crud.get_items(db, skip=skip, limit=limit)
    result = [schemas.UserResponse.model_validate(i).model_dump() for i in items]

    await set_cache(cache_key, result, ttl=120)
    return result


@app.get("/health/")
def get_health():
    return {"status": "ok", "time": datetime.now().isoformat()}
