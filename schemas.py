from pydantic import BaseModel, EmailStr, Field, field_validater
import re
class Signup(BaseModel):
    user_name:str=Field(...,
    min_length=3,
    max_length=20,
    description="a unique name"
    )
    
    email:EmailStr=Field(..., 
    description="a valid email address",
    example="hive@gmail.com"
    )
    
    password:str=Field(...,
    description="create a strong password",
    example="HiveDeveloper3434##what" 
    )
    @field_validater("password")
    @classmethod
    def validate_password(cls, pas):
        if len(pas) <8:
            raise ValueError(
            "password must be at least 8 characters"
            )
        if not pas.searc(r"[A-Z]", pas):
            raise ValueError(
            "password must include at least 1 upper case letter"
            )
        if not re.search(r"\d"):
            raise ValueError(
            "password must include at least 1 digit" 
            )
class Login(BaseModel):
    email:EmailStr=Field(...,) 
    password:str=Field(...,)  
    