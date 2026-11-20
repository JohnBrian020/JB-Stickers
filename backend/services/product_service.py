from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Product


def get_all_products(search=None, category=None, include_inactive=False):
    query = Product.query

    if not include_inactive:
        query = query.filter_by(is_active=True)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if category:
        query = query.filter_by(category=category)

    return query.order_by(Product.created_at.desc()).all()


def get_product_by_id(product_id):
    return db.session.get(Product, product_id)


def create_product(product_data):
    product = Product(**product_data)

    try:
        db.session.add(product)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return product


def update_product(product, product_data):
    try:
        for key, value in product_data.items():
            setattr(product, key, value)

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return product


def delete_product(product):
    try:
        db.session.delete(product)
        db.session.commit()

    except IntegrityError as error:
        db.session.rollback()
        raise ValueError(
            "This product is associated with existing orders "
            "and cannot be deleted."
        ) from error

    except Exception:
        db.session.rollback()
        raise

    return True