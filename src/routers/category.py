from datetime import datetime
from shared.security import get_session
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlmodel import select
from ..utils.models import Category, CategoryBase


router = APIRouter(prefix='/api')



@router.post('/add/category', status_code=201)
async def create_category(dto: CategoryBase, db: Session = Depends(get_session)):
    db_ctg = Category(**dto.dict(), createdAt=datetime.now())
    db.add(db_ctg)
    db.commit()
    db.refresh(db_ctg)
    return db_ctg

@router.get('/see/categories', response_model=List[Category])
async def list_categories(db: Session = Depends(get_session)):
    return db.exec(select(Category)).all()

@router.get('/see/category/{id}', response_model=Category)
async def list_one_category(id: int, db: Session = Depends(get_session)):
    category = db.exec(select(Category).where(Category.categoryId == id)).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return category

@router.put('/update/category/{id}', status_code=200)
async def update_category(id: int, dto: CategoryBase, db: Session = Depends(get_session)):
    category = db.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    for attr, value in dto.dict(exclude_unset=True).items():
        setattr(category, attr, value)
    db.commit()
    db.refresh(category)
    return category

@router.delete('/delete/category/{id}', status_code=204)
async def delete_category(id: int, db: Session = Depends(get_session)):
    category = db.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    db.delete(category)
    db.commit()
    return None


