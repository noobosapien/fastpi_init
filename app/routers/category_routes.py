from fastapi import APIRouter, Depends
from app.schemas.category_schema import CategoryReturn, CategoryCreate
from app.db_connection import get_db_session, SessionLocal
from app.models import Category
from sqlalchemy.orm import Session
from app.utils.category_utils import check_existing_category

router = APIRouter()
db = SessionLocal()


@router.post("/", response_model=CategoryReturn, status_code=201)
def create_category(
    category_data: CategoryCreate, db: Session = Depends(get_db_session)
):
    check_existing_category(db, category_data)
    new_category = Category(**category_data.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category
