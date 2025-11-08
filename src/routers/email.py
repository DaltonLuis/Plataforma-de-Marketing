from ..utils.models import User, VerificationCode
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr
from shared.security import get_hash_password, get_session
from typing import List, Optional
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import secrets
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select, desc
import logging
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix='/api')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'fakedalprogram@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

verification_codes = {}

class EmailSchema(BaseModel):
    subject: str
    message: str
    recipients: List[EmailStr]

class MailSchema(BaseModel):
    code: int
    email: str

class Email(BaseModel):
    email: Optional[str] = None

class ChangePass(BaseModel):
    new_password: str
    conf_new_password: str
    email: str

def generate_verification_code():
    code = secrets.randbelow(10000)
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=20)
    return code, expiration_time

def send_email(email: EmailSchema):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ", ".join(email.recipients)
    msg['Subject'] = email.subject
    msg.attach(MIMEText(email.message, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, email.recipients, msg.as_string())
        server.quit()
        logger.info(f"Email enviado com sucesso para: {', '.join(email.recipients)}")
    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")
        raise HTTPException(status_code=500, detail="Erro ao enviar email")

@router.post("/send_email/")
async def send_email_route(email: EmailSchema, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email)
    return {"message": "Email sent successfully"}


def send_verification_code(email: str, code: int):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg["Subject"] = "Redefinição de Senha"
    
    body = f"Olá,\n\nVocê solicitou a redefinição da sua senha. Por favor, veja o codigo para redefinir sua senha:\n\n{code}\n\nSe você não solicitou a redefinição da sua senha, por favor, ignore este e-mail."
    msg.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
        server.quit()
        logger.info(f"Código de verificação enviado para: {email}")
    except Exception as e:
        logger.error(f"Erro ao enviar código de verificação: {e}")
        raise HTTPException(status_code=500, detail="Erro ao enviar código de verificação")

@router.post("/send-code/")
async def send_code(dto: Email, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.userEmail == dto.email)).first()
    if user:
        code, expiration_time = generate_verification_code()
        send_verification_code(dto.email, code)
        verification_code = VerificationCode(userEmail=dto.email, code=code, expirationTime=expiration_time)
        db.add(verification_code)
        db.commit()
        logger.info(f"Código de verificação gerado para: {dto.email}")
        return {"code": code}
    else:
        raise HTTPException(status_code=404, detail="Email não encontrado.")

@router.post("/verify-code/")
async def verify_code(dto: MailSchema, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.userEmail == dto.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email não encontrado.")
    
    verification_code = db.exec(select(VerificationCode).where(VerificationCode.userEmail == dto.email).order_by(desc(VerificationCode.id))).first()
    if not verification_code:
        raise HTTPException(status_code=400, detail="Não foi gerado nenhum código de verificação para este email.")

    if (int(dto.code) != int(verification_code.code)):
        logger.warning(f"Código de verificação inválido para: {dto.email}")
        raise HTTPException(status_code=400, detail="O código de verificação é inválido.")

    if datetime.now(timezone.utc) > verification_code.expirationTime.replace(tzinfo=timezone.utc):
        logger.warning(f"Código de verificação expirado para: {dto.email}")
        raise HTTPException(status_code=400, detail="O código de verificação expirou.")

    logger.info(f"Código de verificação válido para: {dto.email}")
    return {"detail": "O código de verificação é válido."}



@router.post("/change-password/")
async def change_password(
    dto: ChangePass, db: Session = Depends(get_session)
):
    if dto.new_password != dto.conf_new_password:
        raise HTTPException(status_code=400, detail="As senhas fornecidas não coincidem.")

    user = db.exec(select(User).where(User.userEmail == dto.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email não encontrado.")

    hashed_new_password = get_hash_password(dto.new_password)

    user.password = hashed_new_password
    db.add(user)
    db.commit()
    
    logger.info(f"Senha alterada com sucesso para: {dto.email}")
    return {"detail": "Senha trocada com sucesso."}
