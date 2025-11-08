from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..utils.models import Address, AddressBase
from shared.security import get_session
from datetime import datetime
from typing import List

router = APIRouter(prefix='/api')


@router.get("/see/addresses", response_model=List[Address])
def get_addresses(db: Session = Depends(get_session)):
    return db.query(Address).all()


@router.post("/add/address", status_code=201)
def create_address(address: AddressBase, db: Session = Depends(get_session)):
    db_address = Address(**address.dict(), createdAt=datetime.now())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

@router.get("/see/address/{address_id}", response_model=Address)
def get_address(address_id: int, db: Session = Depends(get_session)):
    address = db.query(Address).filter(Address.adressId == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="O endereço especificado não foi encontrado.")
    return address

@router.put("/update/address/{address_id}", status_code=200)
def update_address(address_id: int, address: AddressBase, db: Session = Depends(get_session)):
    db_address = db.query(Address).filter(Address.adressId == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="O endereço especificado não foi encontrado.")
    for attr, value in address.dict().items():
        setattr(db_address, attr, value)
    db.commit()
    return db_address

@router.delete("/delete/address/{address_id}", status_code=204)
def delete_address(address_id: int, db: Session = Depends(get_session)):
    db_address = db.query(Address).filter(Address.adressId == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(db_address)
    db.commit()
