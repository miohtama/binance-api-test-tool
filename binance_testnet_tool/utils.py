from decimal import Decimal


def quantize_price(price: Decimal, decimals=8) -> Decimal:
    """Always present prices up to certain amount of decimals"""
    return price.quantize((Decimal(10) ** Decimal(-decimals)))
