# app/crud/crud_product.py

from sqlalchemy.orm import Session
from app.models import model
from app.schemas import schema

# --- THIS IS YOUR ORIGINAL CODE (KEEP IT) ---

def get_product(db: Session, product_id: int):
    return db.query(model.Product).filter(model.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schema.ProductBase):
    # This function now correctly uses ProductBase
    db_product = model.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_update: schema.ProductUpdate):
    db_product = get_product(db, product_id=product_id)
    if not db_product:
        return None
    
    update_data = product_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    """
    Deletes a product from the database by its ID.
    """
    db_product = get_product(db, product_id=product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return db_product
    return None # Return None if product not found

def get_product_by_name(db: Session, name: str):
    """
    Fetches a product by its name using a case-insensitive search.
    """
    return db.query(model.Product).filter(model.Product.name.like(f"%{name}%")).first()