import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator
from pymongo import ASCENDING, IndexModel

from joj.horse.odm import Document, Reference, object_id_to_str

UID_RE = re.compile(r'-?\d+')
UNAME_RE = re.compile(r'[^\s\u3000](.{,254}[^\s\u3000])?')


class UserResponse(BaseModel):
    id: str
    _normalize_id = validator('id', pre=True, allow_reuse=True)(object_id_to_str)

    scope: str
    uname: str
    mail: EmailStr

    uname_lower: str = None
    mail_lower: str = None
    gravatar: str = None

    student_id: str = ''
    real_name: str = ''

    salt: str = ''
    hash: str = ''
    role: str = 'user'

    register_timestamp: datetime
    register_ip: str = "0.0.0.0"
    login_timestamp: datetime
    login_ip: str = "0.0.0.0"

    @validator("uname", pre=True)
    def validate_uname(cls, v: str):
        if not UNAME_RE.fullmatch(v):
            raise ValueError('uname')
        return v

    @validator("uname_lower", pre=True, always=True)
    def default_uname_lower(cls, v, *, values, **kwargs):
        return v or values["uname"].strip().lower()

    @validator("mail_lower", pre=True, always=True)
    def default_mail_lower(cls, v, *, values, **kwargs):
        return v or values["mail"].strip().lower()

    @validator("gravatar", pre=True, always=True)
    def default_gravatar(cls, v, *, values, **kwargs):
        return v or values["mail"].strip().lower()

    @validator("register_timestamp", pre=True, always=True)
    def default_register_timestamp(cls, v, *, values, **kwargs):
        return v or datetime.utcnow()

    @validator("login_timestamp", pre=True, always=True)
    def default_login_timestamp(cls, v, *, values, **kwargs):
        return v or datetime.utcnow()


class User(Document, UserResponse):
    class Mongo:
        collection = "users"
        indexes = [
            IndexModel([("scope", ASCENDING), ("uname_lower", ASCENDING)], unique=True),
            IndexModel([("scope", ASCENDING), ("mail_lower", ASCENDING)], unique=True),
        ]

    @classmethod
    async def find_by_uname(cls, scope: str, uname: str) -> 'User':
        return await cls.find_one({'scope': scope, 'uname_lower': uname.strip().lower()})

    @classmethod
    async def login_by_jaccount(cls, student_id: str, jaccount_name: str, real_name: str, ip: str) -> 'User':
        scope = "sjtu"
        user = await cls.find_by_uname(scope=scope, uname=jaccount_name)
        if user:
            user.login_timestamp = datetime.utcnow()
            user.login_ip = ip
            await user.save()
        else:
            user = User(
                scope=scope,
                uname=jaccount_name,
                mail=EmailStr(jaccount_name + "@sjtu.edu.cn"),
                student_id=student_id,
                real_name=real_name,
                register_timestamp=datetime.utcnow(),
                register_ip=ip,
                login_timestamp=datetime.utcnow(),
                login_ip=ip,
            )
            if not await user.insert():
                user = None
        return user


class UserReference(Reference):
    data: Optional[User] = None
    reference = User
