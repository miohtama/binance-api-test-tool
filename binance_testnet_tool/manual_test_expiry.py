"""Manually test expiring limit orders on the spot testnest"""

import sys
import click
import logging
import asyncio

from binance import enums as binance_enums
from binance_testnet_tool.depth import Side, get_depth_info
from binance_testnet_tool.logs import setup_logging
from binance_testnet_tool.main import create_client
from binance_testnet_tool.utils import check_accounted_api_client
from binance_testnet_tool.console import print_colorful_json
from dotenv import load_dotenv

logger = logging.getLogger()


@click.command("Binance order book event expiry test")
@click.option('--api-key', default=None, help='Binance API key', required=False)
@click.option('--api-secret', default=None, help='Binance API secret', required=False)
@click.option('--log-level', default="info", help='Python logging level', required=False)
@click.option('--config-file', default=None, help='Read environment variables from this INI config file', required=False, type=click.Path(exists=True))
def main(api_key, api_secret, log_level, config_file):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_main(api_key, api_secret, log_level, config_file))
    finally:
        print("Done")
        loop.close()


async def _main(api_key, api_secret, log_level, config_file):
    setup_logging(log_level)

    # Read the configuratation
    if config_file:
        load_dotenv(dotenv_path=config_file, verbose=True)
        logger.info("Loaded API keys from %s", config_file)

    network = "spot-testnet"
    client, bm = create_client(api_key, api_secret, network)

    # Subscribe to the events
    check_accounted_api_client(client)
    done_event = asyncio.Event()

    def process_message(msg: dict):
        logger.info("Received event %s", msg["e"])
        print_colorful_json(msg)
        done_event.set()

    logger.info("Connecting to the websocket")

    # start any sockets here, i.e a trade socket
    conn_key = bm.start_user_socket(process_message)
    # then start the socket manager

    logger.info("Connected - stream running - do some orders in another terminal")
    bm.start()

    # Try to create 500 USD order that will get half filled
    market = "BTCUSDT"
    side = Side.ask
    info = get_depth_info(client, market, side)

    if info.empty:
        sys.exit(f"There are no {info.side.value} orders available in the order book to test")

    # Create a limit order or 0.005 that 50% overlaps the top order
    quantity = 0.005
    lot_size = quantity * info.top_order_price
    mid_point = info.top_order_price
    order_start_price = mid_point - lot_size / 2
    order_duration_seconds = 5.0

    print(f"Top {info.side.value} is {info.top_order_price} {info.quote_asset} with the quantity of {info.top_order_quantity} {info.base_asset}")
    print(f"Total {info.cumulative_depth} {info.base_asset} {info.side.value}s at the liquidity of {info.total_liquidity:,} {info.quote_asset}, average price is {info.avg_price} {info.quote_asset}")
    print(f"Creating limit order at {order_start_price} {info.quote_asset} for {quantity} {info.base_asset}")

    # https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md
    # IOC = Immediate or Cancel
    # try to fill as much as possible of the order before cancelling,
    # in this case we should get 50% filled
    order = client.create_order(
        symbol=market,
        side=binance_enums.SIDE_BUY if side == Side.bid else binance_enums.SIDE_SELL,
        type=binance_enums.ORDER_TYPE_LIMIT,
        timeInForce=binance_enums.TIME_IN_FORCE_IOC,
        quantity=str(quantity),
        price=str(order_start_price),
        recvWindow=int(order_duration_seconds * 1000.0))

    print(f"Created order {order}")

    # Wait until we get expiry event
    await done_event.wait()

    # Close websocket listener
    bm.close()







