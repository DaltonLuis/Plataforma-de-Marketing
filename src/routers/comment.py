from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlmodel import Session, select
from shared.security import get_session
from ..utils.models import Comment, CommentReply, CommentBase, CommentReplyBase, User


router = APIRouter(prefix='/api')

##############Comment#############

@router.post("/add/comments/", response_model=Comment)
def create_comment(comment: CommentBase, db: Session = Depends(get_session)):
    db_comment = Comment(**comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/see/comments")
def read_comments(db: Session = Depends(get_session)):
    comments = db.exec(select(Comment).join(User).where(Comment.userId == User.userId)).all()
    formatted_comments = []
    for comment in comments:
        formatted_comment = {
            "commentId": comment.commentId,
            "userId": comment.userId,
            "userFirstName": comment.user.userFirstName,
            "userLastName": comment.user.userLastName,
            "userEmail": comment.user.userEmail,
            "userImage": comment.user.userImage,
            "commentDescription": comment.commentDescription,
            "totalLikes": comment.totalLikes,
            "createdAt": comment.createdAt
        }
        formatted_comments.append(formatted_comment)

    return formatted_comments

@router.get("/see/comment/{commentId}")
def read_comment(commentId: int, db: Session = Depends(get_session)):
    # Ajustar a consulta para selecionar explicitamente Comment e User
    query = select(Comment, User).join(User).where(Comment.commentId == commentId)
    result = db.execute(query).first()
    
    if result is None:
        raise HTTPException(status_code=404, detail="Comentário não encontrado.")
    
    # Descompactar a tupla resultante da consulta
    comment, user = result
    
    formatted_comment = {
        "commentId": comment.commentId,
        "userId": comment.userId,
        "userFirstName": user.userFirstName,
        "userLastName": user.userLastName,
        "userEmail": user.userEmail,
        "userImage": user.userImage,
        "commentDescription": comment.commentDescription,
        "totalLikes": comment.totalLikes,
        "createdAt": comment.createdAt
    }

    return formatted_comment

# Atualiza um comentário
@router.put("/update/comments/{commentId}")
async def update_comment(commentId: int, dto: CommentBase, session: Session = Depends(get_session)):
    comment = session.get(Comment, commentId)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comentário não encontrado.")
    comment.commentDescription = dto.commentDescription
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

@router.delete("/delete/comments/{commentId}", response_model=Comment)
def delete_comment(commentId: int, db: Session = Depends(get_session)):
    db_comment = db.query(Comment).filter(Comment.commentId == commentId).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comentário não encontrado.")
    db.delete(db_comment)
    db.commit()
    return {"Reponse": "Comentário apagado."}

# Curtir uma resposta de comentário
@router.post("/add/comment/{commentId}/like")
async def like_comment_reply(commentId: int, session: Session = Depends(get_session)):
    comment = session.get(Comment, commentId)
    comment.totalLikes = comment.totalLikes + 1
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return {"Response": "Like adicionado"}

######################ComentReply######################

# Atualiza uma resposta de comentário
@router.put("/update/commentReply/{commentReplyId}")
async def update_comment_reply(commentReplyId: int, dto: CommentReplyBase, session: Session = Depends(get_session)):
    reply = session.get(Comment, commentReplyId)
    if reply is None:
        raise HTTPException(status_code=404, detail="Resposta do comentário não encontrada.")
    reply.commentDescription = dto.commentDescription
    session.add(reply)
    session.commit()
    session.refresh(reply)
    return reply

# Curtir uma resposta de comentário
@router.post("/add/commentReply/{commentReplyId}/like")
async def like_comment_reply(commentReplyId: int, session: Session = Depends(get_session)):
    reply = session.get(CommentReply, commentReplyId)
    reply.totalLikes = reply.totalLikes + 1
    session.add(reply)
    session.commit()
    session.refresh(reply)
    return {"Response": "Like adicionado"}

# Exclui uma resposta de comentário
@router.delete("/delete/commentReply/{commentReplyId}")
async def delete_comment_reply(commentReplyId: int, session: Session = Depends(get_session)):
    reply = session.get(CommentReply, commentReplyId)
    if reply is None:
        raise HTTPException(status_code=404, detail="Resposta do comentário não encontrada.")
    session.delete(reply)
    session.commit()
    return {"Response": "Resposta do comentário apagada"}

# Responde a um comentário
@router.post("/add/commentReply/{commentId}")
async def reply_to_comment(commentId: int, dto: CommentReplyBase, session: Session = Depends(get_session)):
    parent_comment = session.get(Comment, commentId)
    if parent_comment is None:
        raise HTTPException(status_code=404, detail="Comentário a ser respondido não encontrado.")
    reply = CommentReply(commentId=commentId, userId=dto.userId, commentDescription=dto.commentDescription)
    session.add(reply)
    session.commit()
    session.refresh(reply)
    return reply

#################Outras##################

# Obtém respostas de comentários de um usuário específico
@router.get("/see/user/{userId}/commentReplied")
async def get_user_comment_replies(userId: int, session: Session = Depends(get_session)):
    replies = session.exec(select(CommentReply).filter(CommentReply.userId == userId)).all()
    return replies

# Obtém comentários em um post específico
# @router.get("/see/post/{postId}/comments")
# async def get_post_comments(postId: int, session: Session = Depends(get_session)):
#     comments = session.exec(select(Comment).filter(Comment.postId == postId)).all()
#     return comments


# Obtém comentários de um usuário específico
@router.get("/users/{userId}/comments")
async def get_user_comments(userId: int, session: Session = Depends(get_session)):
    comments = session.exec(select(Comment).filter(Comment.userId == userId)).all()
    return comments