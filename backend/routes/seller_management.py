from flask import Blueprint, request
from db import db
from models.orm import Seller

bp = Blueprint("seller_management", __name__)

@bp.get("/<name>")
def get_seller(name: str):
    seller = db.get_or_404(Seller, name)

    # Returns capped version of the seller.
    # We don't want to pass the hashed_password neither the last_login to the user.
    return {
        "name": seller.name,
        "created": seller.created,
    }


@bp.post("/")
def create_new_seller():# TODO: Add security to this endpoint
    name     = request.form.get("name")
    password = request.form.get("password")

    db.session.add(Seller(name=name, hashed_password=password))

