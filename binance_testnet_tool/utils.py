from decimal import Decimal


def quantize_price(price, decimals=8) -> Decimal:
    """Always present prices up to certain amount of decimals"""
    return Decimal(price).quantize((Decimal(10) ** Decimal(-decimals)))


def quantize_quantity(quantity, decimals=8) -> Decimal:
    """Always present quantities up to certain amount of decimals

    Binance does not like e.g.:

    quantity=0.00200000000000000004163336342344337026588618755340576171875
    """
    return Decimal(quantity).quantize((Decimal(10) ** Decimal(-decimals)))
