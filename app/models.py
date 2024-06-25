from .db_connection import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    DECIMAL,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(120), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False, server_default="False")
    level = Column(Integer, nullable=False, default="100", server_default="100")
    parent_id = Column(Integer, ForeignKey("category.id"), nullable=True)

    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="category_name_length_check"),
        CheckConstraint("LENGTH(slug) > 0", name="category_slug_length_check"),
        UniqueConstraint("name", "level", name="uq_category_name_level"),
        UniqueConstraint("slug", name="uq_category_slug"),
    )


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, nullable=False)
    pid = Column(
        UUID(as_uuid=True),
        nullable=False,
        server_default=sqlalchemy.text("uuid_generate_v4()"),
    )
    name = Column(String(200), nullable=False)
    slug = Column(String(220), nullable=False)
    description = Column(Text, nullable=True)
    is_digital = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(
        DateTime, nullable=False, server_default=sqlalchemy.text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.text("CURRENT_TIMESTAMP"),
        onupdate=sqlalchemy.func.now(),
    )
    is_active = Column(Boolean, nullable=False, default=False, server_default="false")
    stock_status = Column(
        Enum("oos", "is", "obo", name="status_enum"),
        nullable=False,
        server_default="oos",
    )
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    seasonal_event = Column(Integer, ForeignKey("seasonal_event.id"), nullable=True)

    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="product_name_length_check"),
        CheckConstraint("LENGTH(slug) > 0", name="product_slug_length_check"),
        UniqueConstraint("name", name="uq_product_name"),
        UniqueConstraint("slug", name="uq_product_slug"),
        UniqueConstraint("pid", name="uq_product_pid"),
    )


class ProductLine(Base):
    __tablename__ = "product_line"

    id = Column(Integer, primary_key=True, nullable=False)
    price = Column(DECIMAL(5, 2), nullable=False)
    sku = Column(
        UUID(as_uuid=True),
        nullable=False,
        server_default=sqlalchemy.text("uuid_generate_v4()"),
    )
    stock_qty = Column(Integer, nullable=False, default=0, server_default="0")
    is_active = Column(Boolean, nullable=False, default=False, server_default="false")
    order = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    created_at = Column(
        DateTime, server_default=sqlalchemy.text("CURRENT_TIMESTAMP"), nullable=False
    )
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "price >= 0 AND price <= 999.99", name="product_line_max_value"
        ),
        CheckConstraint(
            '"order" >= 1 AND "order" <= 20', name="product_order_line_range"
        ),
        UniqueConstraint(
            "order", "product_id", name="uq_product_line_order_product_id"
        ),
        UniqueConstraint("sku", name="uq_product_line_sku"),
    )


class ProductImage(Base):
    __tablename__ = "product_image"

    id = Column(Integer, primary_key=True, nullable=False)
    alternative_text = Column(String(100), nullable=False)
    url = Column(String(100), nullable=False)
    order = Column(Integer, nullable=False)
    product_line_id = Column(Integer, ForeignKey("product_line.id"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            '"order" >= 1 AND "order" <= 20', name="product_image_order_range"
        ),
        CheckConstraint(
            "LENGTH(alternative_text) > 0", name="product_image_alt_length"
        ),
        CheckConstraint("LENGTH(url) > 0", name="product_image_url_length"),
        UniqueConstraint("alternative_text", name="uq_product_image_alt"),
    )


class Seasonal(Base):
    __tablename__ = "seasonal_event"

    id = Column(Integer, primary_key=True, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    name = Column(String(100), nullable=False)

    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="seasonal_event_name_length"),
        UniqueConstraint("name", name="uq_seasonal_event_name"),
    )


class Attribute(Base):
    __tablename__ = "attribute"

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(100), nullable=True)

    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="attribute_name_length"),
        UniqueConstraint("name", name="uq_attribute_name"),
    )


class ProductTpye(Base):
    __tablename__ = "product_type"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)
    parent_id = Column(Integer, ForeignKey("product_type.id"), nullable=True)

    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="product_type_name_length_check"),
        UniqueConstraint("name", "level", name="uq_product_type_name_level"),
    )


class AttributeValue(Base):
    __tablename__ = "attribute_value"

    id = Column(Integer, primary_key=True, nullable=False)
    attribute_value = Column(String(100), nullable=False)
    attribute_id = Column(Integer, ForeignKey("attribute.id"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "LENGTH(attribute_value) > 0", name="attribute_value_name_length_check"
        ),
        UniqueConstraint("attribute_id", name="uq_attribute_value_attribute_id"),
    )


class ProductAttributeValue(Base):
    __tablename__ = "product_attribute_value"

    id = Column(Integer, primary_key=True, nullable=False)
    attribute_value_id = Column(
        Integer, ForeignKey("attribute_value.id"), nullable=False
    )
    product_line_id = Column(Integer, ForeignKey("product_line.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("attribute_value_id", name="uq_product_attribute_value"),
    )


class ProductProductType(Base):
    __tablename__ = "product_product_type"

    id = Column(Integer, primary_key=True, nullable=False)
    product_type_id = Column(Integer, ForeignKey("product_type.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "product_type_id", "product_id", name="uq_product_id_product_type_id"
        ),
    )
