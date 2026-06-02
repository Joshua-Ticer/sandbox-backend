import random
from sqlalchemy.orm import Session
from . import models, schemas


def get_item(db: Session, id: int):
    print("DB HIT: get_item")
    return db.query(models.User).filter(models.User.id == id).first()


def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_item(db: Session, item: schemas.UserCreate):
    db_item = models.User(name=item.name, age=item.age, elo=item.elo)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def expected_score(elo_a: int, elo_b: int) -> float:
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


def simulate_match(db: Session, user1_id: int, user2_id: int):
    k_score = 32  # standard ELO constant
    user1 = db.query(models.User).filter(models.User.id == user1_id).first()
    user2 = db.query(models.User).filter(models.User.id == user2_id).first()

    if not user1 or not user2:
        raise ValueError("One or both users not found")

    # expected outcomes
    exp1 = expected_score(user1.elo, user2.elo)
    exp2 = 1 - exp1

    # determine winner (probability based)
    winner = random.random()
    if winner <= exp1:
        score1, score2 = 1, 0
    else:
        score1, score2 = 0, 1

    # elo updates
    user1.elo = round(user1.elo + k_score * (score1 - exp1))
    user2.elo = round(user2.elo + k_score * (score2 - exp2))

    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    return {
        "winner": user1.name if score1 == 1 else user2.name,
        "user1": {"id": user1.id, "elo": user1.elo},
        "user2": {"id": user2.id, "elo": user2.elo},
    }
