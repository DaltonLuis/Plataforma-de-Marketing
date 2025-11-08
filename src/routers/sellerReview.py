from typing import Any, Dict, List, Optional
from src.utils.models import Address, Category, SellerReview, User, Country
from fastapi import APIRouter, Depends, HTTPException
from shared.security import JWTBearer, get_session
from sqlmodel import select, Session
from pydantic import BaseModel


router = APIRouter(prefix='/api')

# Pydantic model
class SellerReviewBase(BaseModel):
    sellerId: Optional[int] = None
    customerReview: Optional[str] = None
    customerId: Optional[int] = None
    rating: Optional[int] = None
    hasRating: Optional[bool] = False

# Conversion function
def convert_to_seller_review(dto: SellerReviewBase) -> SellerReview:
    return SellerReview(
        sellerId=dto.sellerId,
        customerReview=dto.customerReview,
        customerId=dto.customerId,
        rating=dto.rating,
        hasRating=dto.hasRating
    )

# async def get_seller_reviews(db: Session, sellerId: Optional[int] = None):

#     sql_query = db.exec(select(SellerReview))
#     if sellerId:
#         sql_query = db.exec(
#             select(SellerReview)
#             .join(User, User.userId == SellerReview.sellerId)
#             .filter(SellerReview.sellerId == sellerId)
#         )

#     seller_reviews = sql_query.all()

#     formatted_reviews = []

#     for review in seller_reviews:
#         seller_data = db.exec(select(User).where(User.userId == review.sellerId)).first()
#         customer_data = db.exec(select(User).where(User.userId == review.customerId)).first()
#         category_data = db.exec(select(Category).join(User, User.categoryId == Category.categoryId).where(Category.categoryId == seller_data.categoryId)).first()
#         seller_address = db.exec(select(Address).join(User).where(Address.adressId == seller_data.adressId)).first()
#         customer_address = db.exec(select(Address).join(User).where(Address.adressId == customer_data.adressId)).first()
#         my_data = db.exec(select(Country).join(Address).where(Address.countryId == customer_data.adressId)).first()
#         my_data2 = db.exec(select(Country).join(Address).where(Address.countryId == seller_data.adressId)).first()

#         formatted_review = {
#             "sellerReviewId": review.sellerReviewId,
#             "customerReview": review.customerReview,
#             "hasRating": review.hasRating,
#             "rating": review.rating,
#             "#################":"###################",
#             "sellerId": seller_data.userId,
#             "sellerFirstName": seller_data.userFirstName,
#             "sellerLastName": seller_data.userLastName,
#             "sellerEmail": seller_data.userEmail,
#             "sellerType": seller_data.userType,
#             "sellerGender": seller_data.userGender,
#             "sellerPhoneNumber": seller_data.userPhoneNumber,
#             "sellerImage": seller_data.userImage,
#             "sellerCompanyName": seller_data.companyName,
#             "sellerDataOfBirth": seller_data.dateOfBirth,
#             "sellerCategoryId": category_data.categoryId if category_data else None,
#             "sellerCategory": category_data.categoryName if category_data else None,
#             "sellerAdressId": seller_address.adressId if seller_address else None,
#             "sellerCountry": my_data2.countryName if seller_address else None,
#             "sellerDistrict": seller_address.distrit if seller_address else None,
#             "sellerCreatedAt": seller_data.createdAt.isoformat(),
#             "*#######*#########*":"*#########*#########*",
#             "costumerId": customer_data.userId,
#             "costumerFirstName": customer_data.userFirstName,
#             "costumerLastName": customer_data.userLastName,
#             "costumerEmail": customer_data.userEmail,
#             "costumerType": customer_data.userType,
#             "costumerGender": customer_data.userGender,
#             "costumerPhoneNumber": customer_data.userPhoneNumber,
#             "costumerImage": customer_data.userImage,
#             "costumerDataOfBirth": customer_data.dateOfBirth,
#             "costumerAdressId": customer_data.adressId,
#             "costumerCountry":  my_data.countryName,
#             "costumerDistrict":  customer_address.distrit if customer_address else None,
#             "costumerCreatedAt": customer_data.createdAt.isoformat(),
#         }
#         formatted_reviews.append(formatted_review)

#     return formatted_reviews

# @router.get("/see/sellerReviews")
# async def list_seller_reviews(sellerId: Optional[int] = None, db: Session = Depends(get_session)):
#     reviews = await get_seller_reviews(db, sellerId)
#     return reviews

async def get_seller_reviews(db: Session, sellerId: Optional[int] = None) -> List[Dict[str, Any]]:
    sql_query = db.execute(select(SellerReview))
    if sellerId:
        sql_query = db.execute(
            select(SellerReview)
            .join(User, User.userId == SellerReview.sellerId)
            .filter(SellerReview.sellerId == sellerId)
        )

    seller_reviews = sql_query.scalars().all()
    total_customers_reviewed = db.execute(
        select(SellerReview.customerId)
        .distinct()
        .where(SellerReview.sellerId == sellerId)
    ).scalars().all()
    
    # Calcular o total de clientes únicos
    totalCustomers = len(total_customers_reviewed)

    formatted_reviews = []

    for review in seller_reviews:
        seller_data = db.execute(select(User).where(User.userId == review.sellerId)).scalars().first()
        customer_data = db.execute(select(User).where(User.userId == review.customerId)).scalars().first()
        category_data = db.execute(select(Category).join(User, User.categoryId == Category.categoryId).where(Category.categoryId == seller_data.categoryId)).scalars().first()
        seller_address = db.execute(select(Address).join(User).where(Address.adressId == seller_data.adressId)).scalars().first()
        customer_address = db.execute(select(Address).join(User).where(Address.adressId == customer_data.adressId)).scalars().first()
        my_data = db.execute(select(Country).join(Address).where(Address.countryId == customer_data.adressId)).scalars().first()
        my_data2 = db.execute(select(Country).join(Address).where(Address.countryId == seller_data.adressId)).scalars().first()

        formatted_review = {
            "sellerReviewId": review.sellerReviewId,
            "customerReview": review.customerReview,
            "hasRating": review.hasRating,
            "rating": review.rating,
            "#################": "###################",
            "sellerId": seller_data.userId,
            "sellerFirstName": seller_data.userFirstName,
            "sellerLastName": seller_data.userLastName,
            "sellerEmail": seller_data.userEmail,
            "sellerType": seller_data.userType,
            "sellerGender": seller_data.userGender,
            "sellerPhoneNumber": seller_data.userPhoneNumber,
            "sellerImage": seller_data.userImage,
            "sellerCompanyName": seller_data.companyName,
            "sellerDataOfBirth": seller_data.dateOfBirth,
            "sellerCategoryId": category_data.categoryId if category_data else None,
            "sellerCategory": category_data.categoryName if category_data else None,
            "sellerAdressId": seller_address.adressId if seller_address else None,
            "sellerCountry": my_data2.countryName if my_data2 else None,
            "sellerDistrict": seller_address.distrit if seller_address else None,
            "sellerCreatedAt": seller_data.createdAt.isoformat(),
            "*#######*#########*": "*#########*#########*",
            "costumerId": customer_data.userId,
            "costumerFirstName": customer_data.userFirstName,
            "costumerLastName": customer_data.userLastName,
            "costumerEmail": customer_data.userEmail,
            "costumerType": customer_data.userType,
            "costumerGender": customer_data.userGender,
            "costumerPhoneNumber": customer_data.userPhoneNumber,
            "costumerImage": customer_data.userImage,
            "costumerDataOfBirth": customer_data.dateOfBirth,
            "costumerAdressId": customer_data.adressId,
            "costumerCountry": my_data.countryName if my_data else None,
            "costumerDistrict": customer_address.distrit if customer_address else None,
            "costumerCreatedAt": customer_data.createdAt.isoformat(),
        }

        formatted_reviews.append(formatted_review)

    # Adicionar o total de clientes apenas uma vez ao final da lista
    if formatted_reviews:
        formatted_reviews.append({"totalCustomers": totalCustomers})

    return formatted_reviews

@router.get("/see/sellerReviews")
async def list_seller_reviews(sellerId: Optional[int] = None, db: Session = Depends(get_session)):
    reviews = await get_seller_reviews(db, sellerId)
    return reviews

async def get_customer_reviews(db: Session, customerId: Optional[int] = None):

    sql_query = db.exec(select(SellerReview))
    if customerId:
        sql_query = db.exec(
            select(SellerReview)
            .join(User, User.userId == SellerReview.customerId)
            .filter(SellerReview.customerId == customerId)
        )

    customer_reviews = sql_query.all()

    formatted_reviews = []

    for review in customer_reviews:
        seller_data = db.exec(select(User).where(User.userId == review.sellerId)).first()
        customer_data = db.exec(select(User).where(User.userId == review.customerId)).first()
        category_data = db.exec(select(Category).join(User, User.categoryId == Category.categoryId).where(Category.categoryId == seller_data.categoryId)).first()
        seller_address = db.exec(select(Address).join(User).where(Address.adressId == seller_data.adressId)).first()
        customer_address = db.exec(select(Address).join(User).where(Address.adressId == customer_data.adressId)).first()
        my_data = db.exec(select(Country).join(Address).where(Address.countryId == customer_data.adressId)).first()
        my_data2 = db.exec(select(Country).join(Address).where(Address.countryId == seller_data.adressId)).first()


        formatted_review = {
            "sellerReviewId": review.sellerReviewId,
            "customerReview": review.customerReview,
            "hasRating": review.hasRating,
            "rating": review.rating,
            "#################":"###################",
            "costumerId": customer_data.userId,
            "costumerFirstName": customer_data.userFirstName,
            "costumerLastName": customer_data.userLastName,
            "costumerEmail": customer_data.userEmail,
            "costumerType": customer_data.userType,
            "costumerGender": customer_data.userGender,
            "costumerPhoneNumber": customer_data.userPhoneNumber,
            "costumerImage": customer_data.userImage,
            "costumerDataOfBirth": customer_data.dateOfBirth,
            "costumerAdressId": customer_data.adressId,
            "costumerCountry":  my_data.countryName if my_data else None,
            "costumerDistrict":  customer_address.distrit if customer_address else None,
            "costumerCreatedAt": customer_data.createdAt.isoformat(),
            "*#######*#########*":"*#########*#########*",
            "sellerId": seller_data.userId,
            "sellerFirstName": seller_data.userFirstName,
            "sellerLastName": seller_data.userLastName,
            "sellerEmail": seller_data.userEmail,
            "sellerType": seller_data.userType,
            "sellerGender": seller_data.userGender,
            "sellerPhoneNumber": seller_data.userPhoneNumber,
            "sellerImage": seller_data.userImage,
            "sellerCompanyName": seller_data.companyName,
            "sellerDataOfBirth": seller_data.dateOfBirth,
            "sellerCategoryId": category_data.categoryId if category_data else None,
            "sellerCategory": category_data.categoryName if category_data else None,
            "sellerAdressId": seller_address.adressId if seller_address else None,
            "sellerCountry": my_data2.countryName if my_data2 else None,
            "sellerDistrict": customer_address.distrit if customer_address else None,
            "sellerCreatedAt": seller_data.createdAt.isoformat(),
        }
        formatted_reviews.append(formatted_review)

    return formatted_reviews

@router.get("/see/customerReviews")
async def list_buyer_reviews(customerId: Optional[int] = None, db: Session = Depends(get_session)):
    reviews = await get_customer_reviews(db, customerId)
    return reviews

# @router.post('/add/sellerReviews', status_code=201)
# async def create_feedback(dto: SellerReviewBase, db=Depends(get_session)):

#     existing_feedback = db.exec(select(SellerReview).where(
#     (SellerReview.sellerId == dto.sellerId) & (SellerReview.customerId == dto.customerId)
#     )).first()

#     if existing_feedback and existing_feedback.hasRating:
#         raise HTTPException(status_code=400, detail="O comprador já avaliou este vendedor anteriormente.")
#     else:
#         dto.hasRating = True
#         db.add(dto)
#         db.commit()
#         db.refresh(dto)

#     return {'Resultado': 'Avaliação atribuída.'}

@router.post('/add/sellerReviews', status_code=201)
async def create_feedback(dto: SellerReviewBase, db: Session = Depends(get_session)):
    existing_feedback = db.execute(
        select(SellerReview).where(
            (SellerReview.sellerId == dto.sellerId) & (SellerReview.customerId == dto.customerId)
        )
    ).scalars().first()

    if existing_feedback and existing_feedback.hasRating:
        raise HTTPException(status_code=400, detail="O comprador já avaliou este vendedor anteriormente.")
    else:
        dto.hasRating = True
        new_review = convert_to_seller_review(dto)
        db.add(new_review)
        db.commit()
        db.refresh(new_review)

    return {'Resultado': 'Avaliação atribuída.'}

@router.put('/update/sellerReview/{id}', status_code=200)
async def update_feedback(id: int, customerReview: str, rating: int, db: Session = Depends(get_session)):
    existing_feedback = db.get(SellerReview, id)
    if existing_feedback:
        existing_feedback.customerReview = customerReview
        existing_feedback.rating = rating
        db.commit()
        db.refresh(existing_feedback)
        return {"message": "Avaliação de vendedor atualizada com sucesso."}
    else:
        raise HTTPException(status_code=404, detail="Avaliação de vendedor não encontrada.")

@router.delete('/delete/sellerReview/{id}', status_code=204)
async def delete_feedback(id: int, db: Session = Depends(get_session)):
    feedback = db.get(SellerReview, id)
    if feedback:
        db.delete(feedback)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Avaliação de vendedor não encontrada.")



