from pydantic import BaseModel, EmailStr, Field, field_validator
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
    @field_validator("password")
    @classmethod
    def validate_password(cls, pas):
        if len(pas) <8:
            raise ValueError(
            "password must be at least 8 characters"
            )
        if not re.searc(r"[A-Z]", pas):
            raise ValueError(
            "password must include at least 1 upper case letter"
            )
        if not re.search(r"\d", pas):
            raise ValueError(
            "password must include at least 1 digit" 
            )
            
        return pas
class Login(BaseModel):
    email:EmailStr=Field(...,) 
    password:str=Field(...,)  
    
