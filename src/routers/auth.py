import jwt
import logging
from fastapi import APIRouter, Depends, HTTPException
from shared.security import JWTBearer, create_access_token, get_session, verifyPassword, ALGORITHM, JWT_SECRET_KEY
from ..utils.interfacesModel import Login, Token
from passlib.context import CryptContext
from sqlmodel import Session, select
from ..utils.models import User

router = APIRouter(prefix='/api')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post('/user/login')
async def login(dto: Login, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.userEmail == dto.userEmail)).first()
    
    if user is None:
        raise HTTPException(status_code=400, detail="E-mail incorreto.")
    
    if not verifyPassword(dto.password, user.password):
        logger.warning(f"Tentativa de login falhada para o email: {dto.userEmail}")
        raise HTTPException(status_code=400, detail="Senha incorreta.")
    
    access_token = create_access_token(subject=str(user.userId))
    
    user.accessToken = access_token
    db.commit()
    
    logger.info(f"Login bem-sucedido para o usuário: {dto.userEmail}")
    return {"accessToken": access_token}



@router.post('/user/logout')
async def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get('sub')
    
    user = db.get(User, user_id)
    if user:
        user.accessToken = ''
        db.commit()
        logger.info(f"Logout bem-sucedido para o usuário ID: {user_id}")
        return {"message": "Logout Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
