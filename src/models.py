from datetime import datetime

import fastapi
import sqlalchemy
from sqlalchemy import Column, ForeignKey, orm
from sqlalchemy.types import Integer, VARCHAR, Text, DateTime

from src.base.schemas import (
    BodyModUser, DataUser, ResponseUser,
    DataComment, ResponseComment,
    DataPost, ResponsePost
)
from .base import CRUD
from config import Config, logger


BaseModel = orm.declarative_base()
engine = sqlalchemy.create_engine(Config.DATABASE_URL)
session = orm.Session(engine)


class UserModel(BaseModel, CRUD):
    """User model"""
    __tablename__ = "user_model"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    username = Column(VARCHAR(50), unique=True)
    password = Column(VARCHAR(50))
    first_name = Column(VARCHAR(50), nullable=True)
    last_name = Column(VARCHAR(50), nullable=True)

    def __repr__(self):
        return f"{self.username}"

    @staticmethod
    def create(data: BodyModUser) -> bool:
        """Create new user"""
        try:
            session.add(UserModel(
                username=data.username,
                password=data.password,
                first_name=data.firstName,
                last_name=data.lastName
            ))
            session.commit()
            return True
        except Exception as error:
            logger.error(f"{error}")
            session.rollback()
            return False
        finally:
            session.close()

    @staticmethod
    def read(user_id: int) -> ResponseUser:
        try:
            user: UserModel = session.query(UserModel).get(user_id)
            if not user:
                raise NotImplementedError
            return ResponseUser(
                id=user.id,
                username=user.username,
                password=user.password,
                firstName=user.first_name,
                lastName=user.last_name,
            )
        except NotImplementedError:
            raise fastapi.HTTPException(detail="This user does not exist in the system.", status_code=404)
        except Exception as error:
            logger.error(f"{error}")
            raise ValueError("Is there something wrong!")
        finally:
            session.close()

    @staticmethod
    def update(data: DataUser) -> bool:
        try:
            user: UserModel = session.query(UserModel).get(data.userId)
            if not user:
                raise NotImplementedError
            if data.username is not None:
                user.username = data.username
            if data.password is not None:
                user.password = data.password
            if data.firstName is not None:
                user.firstName = data.firstName
            if data.lastName is not None:
                user.lastName = data.lastName
            session.commit()
            return True
        except NotImplementedError:
            raise fastapi.HTTPException(detail="This user was not found.", status_code=404)
        except Exception as error:
            logger.error(f"{error}")
            session.rollback()
            return False
        finally:
            session.close()

    @staticmethod
    def delete(user_id: int) -> bool:
        try:
            session.query(UserModel).filter_by(id=user_id).delete()
            return True
        except Exception as error:
            logger.error(f"{error}")
            return False
        finally:
            session.close()


class PostModel(BaseModel, CRUD):
    """Post model"""
    __tablename__ = "post_model"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    title = Column(VARCHAR(50), default="Not title")
    text = Column(Text, default="Not text")
    create_at = Column(DateTime, default=datetime.now(), nullable=True)
    update_at = Column(DateTime, default=datetime.now(), nullable=True)
    author_id = Column(Integer, ForeignKey("user_model.id", ondelete="SET NULL"), nullable=True, default=None)

    authors = orm.relationship("UserModel", foreign_keys="PostModel.author_id")

    def __repr__(self):
        return f"{self.title}"

    @staticmethod
    def create(data: DataPost) -> bool:
        """Create new post"""
        try:
            session.add(PostModel(
                title=data.title,
                text=data.text,
                author_id=data.authorId,
            ))
            session.commit()
            return True
        except Exception as error:
            logger.error(f"{error}")
            session.rollback()
            return False
        finally:
            session.close()

    @staticmethod
    def read(post_id: int) -> ResponsePost:
        try:
            post: PostModel = session.query(PostModel).get(post_id)
            if not post:
                raise NotImplementedError
            return ResponsePost(
                id=post.id,
                title=post.title,
                text=post.text,
                createAt=post.create_at,
                updateAt=post.update_at,
                authorId=post.author_id,
                comments=[
                    ResponseComment(
                        id=comment.id,
                        text=comment.text,
                        parentId=comment.parent_id,
                        parentCommentId=comment.parent_comment_id,
                        postId=comment.post_id,
                        createAt=comment.create_at,
                        updateAt=comment.update_at,
                        authorId=comment.author_id
                    )
                    for comment in session.query(CommentModel).filter_by(post_id=post.id).all()
                ]
            )
        except NotImplementedError:
            raise fastapi.HTTPException(detail="This post was not found.", status_code=404)
        except Exception as error:
            logger.error(f"{error}")
            raise ValueError("Is there something wrong!")
        finally:
            session.close()

    @staticmethod
    def update(data: DataPost) -> bool:
        try:
            post: PostModel = session.query(PostModel).get(data.postId)
            if not post:
                raise NotImplementedError
            if data.text is not None:
                post.text = data.text
            if data.title is not None:
                post.title = data.title
            post.update_at = datetime.now()
            session.commit()
            return True
        except NotImplementedError:
            raise fastapi.HTTPException(detail="This post was not found.", status_code=404)
        except Exception as error:
            logger.error(f"{error}")
            session.rollback()
            return False
        finally:
            session.close()

    @staticmethod
    def delete(post_id: int) -> bool:
        try:
            session.query(PostModel).filter_by(id=post_id).delete()
            return True
        except Exception as error:
            logger.error(f"{error}")
            return False
        finally:
            session.close()


class CommentModel(BaseModel, CRUD):
    """Comments model"""
    __tablename__ = "comment_model"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    text = Column(Text, default="Not text")
    create_at = Column(DateTime, default=datetime.now(), nullable=True)
    update_at = Column(DateTime, default=datetime.now(), nullable=True)
    parent_comment_id = Column(Integer, nullable=True, default=None)
    parent_id = Column(Integer, ForeignKey("user_model.id", ondelete="SET NULL"), default=None, nullable=True)
    post_id = Column(Integer, ForeignKey("post_model.id", ondelete="CASCADE"))
    author_id = Column(Integer, ForeignKey("user_model.id", ondelete="SET NULL"))

    parents = orm.relationship("UserModel", foreign_keys="CommentModel.parent_id")
    authors = orm.relationship("UserModel", foreign_keys="CommentModel.author_id")
    posts = orm.relationship('PostModel', foreign_keys="CommentModel.post_id")

    def __repr__(self):
        return f"{self.post_id}@{self.author_id}"

    @staticmethod
    def create(data: DataComment) -> bool:
        """Create new comment"""
        try:
            session.add(CommentModel(
                text=data.text,
                parent_id=data.parentId,
                post_id=data.postId,
                author_id=data.authorId,
            ))
            session.commit()
            return True
        except Exception as error:
            logger.error(f"{error}")
            session.rollback()
            return False
        finally:
            session.close()

    @staticmethod
    def read(comment_id: int) -> ResponseComment:
        try:
            comment: CommentModel = session.query(CommentModel).get(comment_id)
            if not comment:
                raise NotImplementedError
            return ResponseComment(
                id=comment.id,
                text=comment.text,
                parentId=comment.parent_id,
                parentCommentId=comment.parent_comment_id,
                postId=comment.post_id,
                createAt=comment.create_at,
                updateAt=comment.update_at,
                authorId=comment.author_id
            )
        except NotImplementedError:
            raise fastapi.HTTPException(detail="This comment was not found!", status_code=404)
        except Exception as error:
            logger.error(f"{error}")
            raise ValueError("Is there something wrong!")
        finally:
            session.close()

    @staticmethod
    def update(data: DataComment) -> bool:
        try:
            comment: CommentModel = session.query(CommentModel).get(data.commentId)
            if not comment:
                raise NotImplementedError
            if data.text is not None:
                comment.text = data.text
            comment.update_at = datetime.now()
            session.commit()
            return True
        except NotImplementedError:
            raise fastapi.HTTPException(detail="This comment was not found.", status_code=404)
        except Exception as error:
            logger.error(f"{error}")
            session.rollback()
            return False
        finally:
            session.close()

    @staticmethod
    def delete(comment_id: int) -> bool:
        try:
            session.query(CommentModel).filter_by(id=comment_id).delete()
            return True
        except Exception as error:
            logger.error(f"{error}")
            return False
        finally:
            session.close()


def create_db():
    """Create database and his tables"""
    BaseModel.metadata.create_all(engine)
