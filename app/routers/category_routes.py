from fastapi import APIRouter, Depends, HTTPException
from app.schemas.category_schema import (
    CategoryReturn,
    CategoryDeleteReturn,
    CategoryCreate,
    CategoryUpdate,
)
from app.db_connection import get_db_session, SessionLocal
from app.models import Category
from sqlalchemy.orm import Session
from app.utils.category_utils import check_existing_category
import logging
from typing import List


router = APIRouter()
db = SessionLocal()
logger = logging.getLogger("app")


@router.post("/", response_model=CategoryReturn, status_code=201)
def create_category(
    category_data: CategoryCreate, db: Session = Depends(get_db_session)
):
    try:
        check_existing_category(db, category_data)
        new_category = Category(**category_data.model_dump())
        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return new_category

    except HTTPException as http_exc:
        logger.error(f"Error while retrieving category bu slug: {http_exc}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while creating category: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# get
@router.get("/", response_model=List[CategoryReturn])
def get_categories(db: Session = Depends(get_db_session)):
    try:
        categories = db.query(Category).all()
        return categories
    except Exception as e:
        logger.error(f"Unexpected error while retriving categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/slug/{category_slug}", response_model=CategoryReturn)
def get_category_by_slug(category_slug: str, db: Session = Depends(get_db_session)):
    try:
        category = db.query(Category).filter(Category.slug == category_slug).first()

        if not category:
            raise HTTPException(status_code=404, detail="Category does not exist")

        return category

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error while retriving categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{category_id}", response_model=CategoryReturn, status_code=201)
def updateCategory(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db_session),
):
    try:
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        for key, value in category_data.model_dump().items():
            setattr(category, key, value)

        db.commit()
        db.refresh(category)
        return category
    except HTTPException as http_exc:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while updating category: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{category_id}", response_model=CategoryDeleteReturn)
def delete_category(category_id: int, db: Session = Depends(get_db_session)):
    try:
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        db.delete(category)
        db.commit()

        return category

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while deleting category: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
