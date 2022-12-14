from typing import List

from fastapi import APIRouter, Depends, Request, HTTPException

from ..auth import JWTBearer, AutoHandler
from ..models import PostModel, CommentModel, session
from ..base.schemas import BodyModPost, DataPost, QueryPost, ResponsePost, ResponseStatus, ResponseComment


router = APIRouter(
    prefix="/post",
    tags=["Post"]
)


@router.get(
    "/user/all",
    dependencies=[Depends(JWTBearer())],
    response_model=List[ResponsePost]
)
async def get_all_posts_by_user_id(request: Request):
    """
    Get all post by user id
    """
    user_id = AutoHandler.decode_jwt_token(request.headers.get("Authorization").split(" ")[1])["userId"]
    return [
        ResponsePost(
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
                    parentId=comment.create_at,
                    parentCommentId=comment.parent_comment_id,
                    postId=comment.update_at,
                    createAt=comment.parent_id,
                    updateAt=comment.post_id,
                    authorId=comment.author_id
                )
                for comment in session.query(CommentModel).filter_by(post_id=post.id).all()
            ]
        )
        for post in session.query(PostModel).filter_by(author_id=user_id).all()
    ]


@router.get(
    "/all/",
    response_model=List[ResponsePost]
)
async def get_all_posts():
    """
    Get all posts
    """
    return [
        ResponsePost(
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
                    parentCommentId=comment.parent_comment_id,
                    parentId=comment.parent_id,
                    postId=comment.post_id,
                    createAt=comment.create_at,
                    updateAt=comment.update_at,
                    authorId=comment.author_id
                )
                for comment in session.query(CommentModel).filter_by(post_id=post.id).all()
            ]
        )
        for post in session.query(PostModel).all()
    ]


@router.post(
    "/",
    dependencies=[Depends(JWTBearer())],
    response_model=ResponseStatus
)
async def create_post(request: Request, body: BodyModPost):
    """
    Create new post

    - **title**: post title (optional)
    - **text**: post text (optional)
    """
    return ResponseStatus(status=PostModel.create(data=DataPost(
        title=body.title,
        text=body.text,
        authorId=AutoHandler.decode_jwt_token(request.headers.get("Authorization").split(" ")[1])["userId"]
    )))


@router.get(
    "/",
    response_model=ResponsePost
)
async def get_post(query: QueryPost = Depends()):
    """
    Get post by id

    - **postId**: post id
    """
    return PostModel.read(query.postId)


@router.put(
    "/",
    dependencies=[Depends(JWTBearer())],
    response_model=ResponseStatus
)
async def update_post(request: Request, body: BodyModPost, query: QueryPost = Depends()):
    """
    Update post

    - **title**: post title (optional)
    - **text**: post text (optional)
    """
    user_id = AutoHandler.decode_jwt_token(request.headers.get("Authorization").split(" ")[1])["userId"]
    if PostModel.read(query.postId).authorId != user_id:
        raise HTTPException(detail="You are not the owner of the post!", status_code=401)
    return ResponseStatus(status=PostModel.update(data=DataPost(
        title=body.title,
        text=body.text,
        postId=query.postId
    )))


@router.delete(
    "/",
    dependencies=[Depends(JWTBearer())],
    response_model=ResponsePost
)
async def delete_post(request: Request, query: QueryPost = Depends()):
    """
    Delete post by id

    - **postId**: post id
    """
    user_id = AutoHandler.decode_jwt_token(request.headers.get("Authorization").split(" ")[1])["userId"]
    if PostModel.read(query.postId).authorId != user_id:
        raise HTTPException(detail="You are not the owner of the post!", status_code=401)
    return PostModel.delete(query.postId)
