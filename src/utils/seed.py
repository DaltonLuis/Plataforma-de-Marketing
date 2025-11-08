from ..utils.models import Address, Category, User, VerificationCode, SellerReview, Country, Product, Post, ProductReview
from shared.security import get_session
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from passlib.hash import pbkdf2_sha256
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INITIAL_DATA = {
    'Country': [
        {"countryName": "São Tomé e Príncipe"}
    ],
    'Address': [
        {"distrit": "Água Grande", "countryId": 1},
        {"distrit": "Cantagalo", "countryId": 1},
        {"distrit": "Caué", "countryId": 1},
        {"distrit": "Lembá", "countryId": 1},
        {"distrit": "Lobata", "countryId": 1},
        {"distrit": "Mé-Zóchi", "countryId": 1},
        {"distrit": "Região Autónoma do Príncipe", "countryId": 1},
    ],  
    'Category': [
        {"categoryName": "Serviços de Pintura"},
        {"categoryName": "Serviços de Encanamento"},
        {"categoryName": "Serviços de Limpeza"},
        {"categoryName": "Serviços de Jardinagem"},
        {"categoryName": "Serviços de Elétrica"},
        {"categoryName": "Serviços de Construção Civil"},
        {"categoryName": "Serviços de Mudança"},
        {"categoryName": "Serviços de Reparo de Automóveis"},
        {"categoryName": "Serviços de Instalação de Ar Condicionado"}
    ],
    'User': [
        {
            "userFirstName": "Aewon",
            "userLastName": "Vaz",
            "userEmail": "adminaewon@gmail.com",
            "userType": "Admin",
            "password": "admin",
            "userGender": "Masculino",
            "userPhoneNumber": "9999999",
            "userImage": "",
            "companyName": "ProcuraAqui",
            "dateOfBirth": "",
            "description": "Administrador da plataforma ProcuraAqui",
            "adressId": 1
        },
        {
            "userFirstName": "Dalton",
            "userLastName": "Luis",
            "userEmail": "admindalton@gmail.com",
            "userType": "Admin",
            "password": "admin",
            "userGender": "Masculino",
            "userPhoneNumber": "9999899",
            "userImage": "",
            "companyName": "ProcuraAqui",
            "dateOfBirth": "",
            "description": "Administrador da plataforma ProcuraAqui",
            "adressId": 1
        },
        {
            "userFirstName": "Leonelsio",
            "userLastName": "Varela",
            "userEmail": "adminvarela@gmail.com",
            "userType": "Admin",
            "password": "admin",
            "userGender": "Masculino",
            "userPhoneNumber": "9999799",
            "userImage": "",
            "companyName": "ProcuraAqui",
            "dateOfBirth": "",
            "description": "Administrador da plataforma ProcuraAqui",
            "adressId": 1
        },
        {
            "userFirstName": "Vendedor",
            "userLastName": "Teste",
            "userEmail": "vendedor@gmail.com",
            "userType": "Seller",
            "password": "vendedor",
            "userGender": "Masculino",
            "userPhoneNumber": "",
            "userImage": "",
            "companyName": "ProcuraAqui",
            "dateOfBirth": "",
            "description": "Vendedor na plataforma ProcuraAqui",
            "adressId": 1
        },
        {
            "userFirstName": "Cliente",
            "userLastName": "Teste",
            "userEmail": "cliente@gmail.com",
            "userType": "Buyer",
            "password": "cliente",
            "userGender": "Masculino",
            "userPhoneNumber": "",
            "userImage": "",
            "companyName": "ProcuraAqui",
            "dateOfBirth": "",
            "description": "Comprador na plataforma ProcuraAqui",
            "adressId": 1
        }
    ],
    'Product': [
        {"productName": "Produto 1", "productDescription": "Descrição do Produto 1", "quantity": 10, "unitPrice": 100.0, "unitInStock": 5, "unitInOrder": 0, "picture": "", "categoryId": 1},
        {"productName": "Produto 2", "productDescription": "Descrição do Produto 2", "quantity": 20, "unitPrice": 200.0, "unitInStock": 10, "unitInOrder": 0, "picture": "", "categoryId": 2},
        {"productName": "Produto 3", "productDescription": "Descrição do Produto 3", "quantity": 30, "unitPrice": 300.0, "unitInStock": 15, "unitInOrder": 0, "picture": "", "categoryId": 3}
    ]
}

MODEL_MAP = {
    'Country': Country,
    'Address': Address,
    'Category': Category,
    'User': User,
    'Product': Product
}

def _check_if_record_exists(db: Session, model, data: dict, model_name: str) -> bool:
    if model_name == 'User':
        return db.exec(select(model).where(model.userEmail == data.get("userEmail"))).first() is not None
    elif model_name == 'Country':
        return db.exec(select(model).where(model.countryName == data.get("countryName"))).first() is not None
    elif model_name == 'Category':
        return db.exec(select(model).where(model.categoryName == data.get("categoryName"))).first() is not None
    elif model_name == 'Address':
        return db.exec(select(model).where(
            model.distrit == data.get("distrit"),
            model.countryId == data.get("countryId")
        )).first() is not None
    elif model_name == 'Product':
        return db.exec(select(model).where(model.productName == data.get("productName"))).first() is not None
    return False

def initialize_tables(db: Session = Depends(get_session)):
    logger.info("Iniciando seed do banco de dados...")
    total_added = 0
    total_skipped = 0
    
    try:
        for model_name, data_list in INITIAL_DATA.items():
            model = MODEL_MAP.get(model_name)
            if not model:
                logger.warning(f"Modelo {model_name} não encontrado no mapeamento")
                continue
            
            logger.info(f"Processando tabela {model_name}...")
            items_to_add = []
            
            for data in data_list:
                if _check_if_record_exists(db, model, data, model_name):
                    identifier = data.get("userEmail") or data.get("countryName") or data.get("categoryName") or data.get("distrit") or data.get("productName")
                    logger.debug(f"Registro '{identifier}' já existe em {model_name}, pulando...")
                    total_skipped += 1
                    continue
                
                if model_name == 'User':
                    data_copy = data.copy()
                    hashed_password = pbkdf2_sha256.hash(data_copy["password"])
                    data_copy["password"] = hashed_password
                    items_to_add.append(model(**data_copy))
                else:
                    items_to_add.append(model(**data))
            
            if items_to_add:
                db.add_all(items_to_add)
                db.commit()
                total_added += len(items_to_add)
                logger.info(f"✓ {len(items_to_add)} registro(s) adicionado(s) à tabela {model_name}")
            else:
                logger.info(f"✓ Nenhum registro novo para adicionar em {model_name}")
        
        if total_added > 0:
            logger.info(f"Seed concluído! Total: {total_added} registros adicionados, {total_skipped} já existentes")
        else:
            logger.info(f"Seed concluído! Base de dados já está populada ({total_skipped} registros existentes)")
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Erro de integridade ao popular banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro de integridade no banco de dados")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao popular banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")
