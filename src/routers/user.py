import os
import re
import jwt
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form
from shared.security import JWTBearer, ALGORITHM, JWT_SECRET_KEY, get_session, get_hash_password
from sqlmodel import Session, select
from ..utils.models import Address, Category, User, UserBase, Country
from .sellerReview import get_seller_reviews

router = APIRouter(prefix='/api')

current_directory = Path(os.getcwd())
EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
ALLOWED_USER_TYPES = {"Buyer", "Seller", "Admin"}


# Função para salvar a imagem em uma pasta
def save_image(file: UploadFile, folder_name: str, user_id: int) -> str:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    filename = f"{user_id}_{file.filename}"
    file_path = os.path.join(folder_name, filename) # type: ignore
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return file_path

# Função para verificar se o tipo de arquivo é válido
def is_valid_file_type(filename: str):
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    ext = os.path.splitext(filename)[1]
    return ext.lower() in valid_extensions

@router.get('/see/users')
async def list_users(user_id: Optional[int] = None, db: Session = Depends(get_session)):

    query = None
    if user_id:
        query = select(User).where(User.userId == user_id)
        # If querying by user_id, build a query to fetch a single user
        user = db.exec(query).first()
        # Execute the query and fetch the first result
        users = [user] if user else []
        # Convert the result to a list to iterate over later
    else:
        query = select(User)
        # If not querying by user_id, build a query to fetch all users
        users = db.exec(query).all()
        # Execute the query and fetch all results

    users_data = []

    for user in users:
        category_data = None
        if user.categoryId:
            category_data = db.exec(select(Category).where(Category.categoryId == user.categoryId)).first()

        address_data = None
        if user.adressId:
            address_data = db.exec(select(Address).where(Address.adressId == user.adressId)).first()
            my_data = db.exec(select(Country).join(Address).where(Address.adressId == address_data.adressId)).first()

        formatted_user = {
            "userId": user.userId,
            "userFirstName": user.userFirstName,
            "userLastName": user.userLastName,
            "userEmail": user.userEmail,
            "userType": user.userType,
            "userGender": user.userGender,
            "userPhoneNumber": user.userPhoneNumber,
            "userImage": user.userImage,
            "companyName": user.companyName,
            "dateOfBirth": user.dateOfBirth,
            "description": user.description,
            "categoryId": user.categoryId,
            "category": category_data.categoryName if category_data else "",
            "addressId": user.adressId,
            "country": my_data.countryName if my_data else "",
            "district": address_data.distrit if address_data else "",
            "createdAt": user.createdAt.isoformat() if user.createdAt else "",
            "reviewsReceived": await get_seller_reviews(db, user.userId)
        }
        users_data.append(formatted_user)
    
    return users_data



@router.post('/add/user', status_code=201)
async def add_user(dto: UserBase,  db: Session = Depends(get_session)):

    if not dto.userEmail or not EMAIL_REGEX.match(dto.userEmail):
        raise HTTPException(status_code=400, detail='O email fornecido não é válido.')
    
    if dto.userType not in ALLOWED_USER_TYPES:
        raise HTTPException(status_code=400, detail='O tipo de utilizador fornecido não é válido.')

    email_exists = db.exec(select(User).where(User.userEmail == dto.userEmail)).first()
    if email_exists:
        raise HTTPException(status_code=400, detail='O email já está registrado.')
    hashed_password = get_hash_password(dto.password)
    user_data = dto.dict()
    user_data['password'] = hashed_password
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {'Resultado': 'Utilizador adicionado.'}


@router.put('/update/user/{id}/image', status_code=200)
async def update_user(
    id: int,
    userImage: UploadFile = File(None),
    db=Depends(get_session)
):
    user1 = db.get(User, id)

    if not user1:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado.")
    
    if userImage is not None:

        if not is_valid_file_type(userImage.filename):
            raise HTTPException(status_code=400, detail="Tipo de arquivo inválido. Apenas arquivos de imagem são permitidos.")
        
        if user1.userType.lower():
            file_path = save_image(userImage, f"{user1.userType.lower()}_images", id)

        image_path = os.path.join(f'{current_directory}/', file_path)
     
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Imagem não encontrada.")

        user1.userImage = f"http://localhost:5000/{file_path}"

    db.commit()
    db.refresh(user1)
    return user1

@router.put('/update/user/{id}', status_code=200)
async def update_user(
    id: int,
    # userFirstName: Optional[str] = Form(None),
    # userLastName: Optional[str] = Form(None),
    # userEmail: str = Form(None),
    # userType: Optional[str] = Form(None),
    # userGender: Optional[str] = Form(None),
    # userPhoneNumber: Optional[str] = Form(None),
    # companyName: Optional[str] = Form(None),
    # dateOfBirth: Optional[str] = Form(None),
    # description: Optional[str] = Form(None),
    # adressId: Optional[int] = Form(None),
    # categoryId: Optional[int] = Form(None),
    dto: UserBase,
    db=Depends(get_session)
):
    user1 = db.get(User, id)
    dto_dict = {
        "userFirstName": dto.userFirstName,
        "userLastName": dto.userLastName,
        "userEmail": dto.userEmail,
        "userType": dto.userType,
        "userGender": dto.userGender,
        "userPhoneNumber": dto.userPhoneNumber,
        "companyName": dto.companyName,
        "dateOfBirth": dto.dateOfBirth,
        "description": dto.description,
        "adressId": dto.adressId,
        "categoryId": dto.categoryId
    }
    dto_dict_filtered = {key: value for key, value in dto_dict.items() if value is not None}

    if not user1:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado.")

    for key, value in dto_dict_filtered.items():
        setattr(user1, key, value)  # Atualiza os atributos do usuário com os valores fornecidos
    
    db.commit()
    db.refresh(user1)
    return user1


@router.delete('/delete/user/{id}', status_code=204)
async def delete_user(id: int,  db: Session = Depends(get_session)):
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    db.delete(user)
    db.commit()
    return None

@router.get("/users/me")
async def get_user_info(current_user_id: int = Depends(JWTBearer()),  db: Session = Depends(get_session)):
    try:
        payload = jwt.decode(current_user_id, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        user = db.exec(select(User).where(User.userId == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilizado inexistente")
    except jwt.PyJWKError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user



@router.get("/see/sellers_by_category/{category_name}")
async def get_sellers_by_category(category_name: str, db = Depends(get_session)):
    # Realiza um join entre as tabelas User e Category usando SQLModel
    query = select(User, Category).join(Category).where(Category.categoryName == category_name)
    
    # Executa a consulta e retorna o primeiro resultado
    user_category = db.exec(query).first()
    
    # Verifica se a categoria foi encontrada
    if not user_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Retorna os usuários que pertencem à categoria especificada
    users_in_category = db.exec(select(User).where(User.categoryId == user_category.Category.categoryId)).all()
    
    return users_in_category
