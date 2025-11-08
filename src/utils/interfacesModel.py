from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from shared.security import get_hash_password


class Token(BaseModel):
    accessToken: Optional[str] = None

class Login(BaseModel):
    userEmail: Optional[str] = None
    password: Optional[str] = None

class UserBase(BaseModel):
    userFirstName: Optional[str] = None
    userLastName: Optional[str] = None
    userEmail: Optional[str] = None
    userType: Optional[str] = None
    password: Optional[str] = None or Field(alias='password')
    userGender: Optional[str] = None
    userPhoneNumber: Optional[str] = None
    userImage: Optional[str] = None 
    companyName: Optional[str] = None
    dateOfBirth: Optional[datetime] = None
    description: Optional[str] = None
    adressId: Optional[int] = None
    categoryId: Optional[int] = None

    @validator('password', pre=True)
    def hash_the_password(cls, v):
        return get_hash_password(v)
    
class UserWithoutPass(BaseModel):
    userFirstName: Optional[str] = None
    userLastName: Optional[str] = None
    userEmail: Optional[str] = None
    userType: Optional[str] = None
    userGender: Optional[str] = None
    userPhoneNumber: Optional[str] = None
    userImage: Optional[str] = None 
    companyName: Optional[str] = None
    dataOfBirth: Optional[str] = None
    description: Optional[str] = None
    adressId: Optional[int] = None
    categoryId: Optional[int] = None
