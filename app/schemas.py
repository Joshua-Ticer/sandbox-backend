from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    name: str
    age: int
    elo: int

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

