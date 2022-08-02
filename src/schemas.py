from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, validator


class BodyUser(BaseModel):
    username: str = Field(description="Username", max_length=50)
    password: str = Field(description="Password", max_length=50)
    firstName: Optional[str] = Field(description="First name", max_length=50, default=None)
    lastName: Optional[str] = Field(description="Last name", max_length=50, default=None)

    @validator("username")
    def valid_username(cls, username: str):
        pass

    @validator("firstName")
    def valid_first_name(cls, first_name: str):
        pass

    @validator("lastName")
    def valid_last_name(cls, last_name: str):
        pass


class BodyCreatePost(BaseModel):
    title: Optional[str] = Field(description="Post title", max_length=50, default=None)
    text: Optional[str] = Field(description="Post text", default=None)
    authorId: int = Field(description="Post author")

    @validator("authorId")
    def valid_author_id(cls, author_id: int):
        pass

    @validator("title")
    def valid_title_id(cls, title: str):
        pass

    @validator("text")
    def valid_text_id(cls, text: str):
        pass


class BodyCreateComment(BaseModel):
    text: str
    parentId: int
    postId: int
    authorId: int
