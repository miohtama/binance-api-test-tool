"""Binance spot testnet depth tools."""
import enum
import logging
from binance.client import Client

from dataclasses import dataclass


logger = logging.getLogger()


class Side(enum.Enum):
    ask = "ask"
    bid = "bid"


@dataclass
class SideDepthInfo:
    total_liquidity: float = 0
    cumulative_depth: float = 0
    avg_price: float = 0
    top_order_price: float = 0
    top_order_quantity: float = 0
    market_order_name: str = None
    empty: bool = None
    side: Side = None
    base_asset: str = None
    quote_asset: str = None


def get_depth_info(client: Client, market: str, side: Side) -> SideDepthInfo:
    """Extract some simple depth information about the visible order book."""

    info = SideDepthInfo(side=side)
    pair_info = client.get_symbol_info(market)

    info.base_asset = pair_info["baseAsset"]
    info.quote_asset = pair_info["quoteAsset"]

    depth = client.get_order_book(symbol=market)

    if side == Side.ask:
        side_data = sorted(depth["asks"], key=lambda x: float(x[0]))
    elif side == Side.bid:
        side_data = sorted(depth["bids"], key=lambda x: -float(x[0]))
    else:
        raise RuntimeError(f"Unknown side {side}")

    info.market_order_name = "market buy" if side == Side.ask else "market sell"

    if not side_data:
        info.empty = True
    else:
        top, top_quantity = side_data[0]
        info.top_order_price = float(top)
        info.top_order_quantity = float(top_quantity)
        cumulative_depth = total_liquidity = 0
        for price, quantity in side_data:
            price = float(price)
            quantity = float(quantity)
            total_liquidity += price * quantity
            cumulative_depth += quantity

        info.avg_price = total_liquidity / cumulative_depth
        info.cumulative_depth = cumulative_depth
        info.total_liquidity = total_liquidity

    return info
