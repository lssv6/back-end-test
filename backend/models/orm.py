import phonenumbers

from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import validates

from sqlalchemy.sql import func

from datetime import datetime

class Base(DeclarativeBase):
    """Base class for all the other ORM models."""
    pass


class Seller(Base):
    __tablename__ = "SELLER"

    name           : Mapped[str] = mapped_column(String(42), primary_key=True,)
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False)
    created        : Mapped[datetime] = mapped_column(DateTime(timezone=True), insert_default=func.now())
    last_login     : Mapped[datetime] = mapped_column(DateTime(timezone=True))

class SoldDIDNumber(Base):
    __tablename__ = "SOLD_DID_NUMBERS"
    did_id    : Mapped[str] = mapped_column(ForeignKey("DID_NUMBERS.id"), primary_key=True)
    seller    : Mapped[str] = mapped_column(ForeignKey("SELLER.name"))
    
    sold_at   : Mapped[datetime] = mapped_column(DateTime(timezone=True), insert_default=func.now())

class DIDNumber(Base):
    """ORM-schema for numbers that are for sale"""
    __tablename__ = "DID_NUMBERS"

    id         : Mapped[int] = mapped_column(primary_key=True)
    cellphone  : Mapped[str] = mapped_column(String(20))
    monthyPrice: Mapped[str] = mapped_column(String())
    setupPrice : Mapped[int] = mapped_column(String())
    currency   : Mapped[str] = mapped_column(String(3)) # FIXME: As stated in the README, it must be a string, but I should change futhermore for 
    
    def _format_price_str(self, price: str) -> str:
        """This function test if the string is formatted in the specified format:"""
        sep_by_dot = price.split(".")
        
        assert len(sep_by_dot) == 2, "The price must have two parts: <Integer>.<Fractional>"
        assert sep_by_dot[0].isdigit, "Integer part of the price must be only digits"
        assert sep_by_dot[1].isdigit, "Fractional part of the price must be only digits"

        sep_by_dot[1] = sep_by_dot[1].zfill(2)
    
        return ".".join(sep_by_dot)
    
    def _validate_price(self, price: int | float | str) -> str:
        """Validates the given price to an valid string if possible."""
        if isinstance(price, str):
            return self._format_price_str(price)
        
        if isinstance(price, (int, float)):
            price = str(float(price))
        return self._format_price_str(price)

    @validates("monthyPrice")
    def validate_monthyPrice(self, key, monthyPrice):
        """Prevents the insertion of wrong Prices. Such as: -0.9, 0.99.1 , etc"""
        return self._validate_price(monthyPrice)
    
    @validates("setupPrice")
    def validate_setupPrice(self, key, setupPrice):
        """Prevents the insertion of wrong Prices. Such as: -0.9, 0.99.1 , etc"""
        return self._validate_price(setupPrice)

    @validates("cellphone")
    def validate_value(self, key, cellphone):
        """Prevents the insertion of wrong and malformatted numbers in the database.
        If the value is malformed, an exception is thrown and the insertion of the row is
        denied.
        """
        assert phonenumbers.is_valid_number(cellphone), f"{cellphone=} isnt an valid cellphone number."
        
        # If the number is valid, let's standardize it.
        parsed_number = phonenumbers.parse(cellphone)
        international_format = phonenumbers.PhoneNumberFormat.INTERNATIONAL
        formated_number = phonenumbers.format_number(parsed_number, international_format)

        # Will return the valid cellphone into an better standardized version.
        return formated_number
