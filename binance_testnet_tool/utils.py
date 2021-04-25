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


# TODO: Make this generic "get_filter_param"
def get_tick_size(client, market: str) -> Decimal:
    """Get a tick size.

    If we try to post a too accurate order (decimals more than a tick size), we get::

        binance.exceptions.BinanceAPIException: APIError(code=-1013): Filter failure: MARKET_LOT_SIZE

    :return: Decimal("0.00001")
    """
    info = client.get_symbol_info(market)
    filters = {f["filterType"]: f for f in info["filters"]}
    # This is like "0.00001000"
    tick_size = filters["PRICE_FILTER"]["tickSize"]
    return Decimal(tick_size)