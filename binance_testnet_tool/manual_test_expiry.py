"""Manually test expiring limit orders on the spot testnest"""

import sys
import time
import uuid

import click
import logging

from binance import enums as binance_enums
from binance_testnet_tool.depth import Side, get_depth_info
from binance_testnet_tool.logs import setup_logging
from binance_testnet_tool.main import create_client
from binance_testnet_tool.utils import check_accounted_api_client, quantize_price
from binance_testnet_tool.console import print_colorful_json
from dotenv import load_dotenv

logger = logging.getLogger()


@click.command("Binance order book event expiry test")
@click.option('--api-key', default=None, help='Binance API key', required=False)
@click.option('--api-secret', default=None, help='Binance API secret', required=False)
@click.option('--log-level', default="info", help='Python logging level', required=False)
@click.option('--config-file', default=None, help='Read environment variables from this INI config file', required=False, type=click.Path(exists=True))
def main(api_key, api_secret, log_level, config_file):
    _main(api_key, api_secret, log_level, config_file)


def _main(api_key, api_secret, log_level, config_file):
    setup_logging(log_level)

    # Read the configuratation
    if config_file:
        load_dotenv(dotenv_path=config_file, verbose=True)
        logger.info("Loaded API keys from %s", config_file)

    network = "spot-testnet"
    client, bm = create_client(api_key, api_secret, network)

    # Subscribe to the events
    check_accounted_api_client(client)
    done = False

    def process_message(msg: dict):
        nonlocal done
        nonlocal order_id
        logger.info("Received event %s", msg["e"])
        print_colorful_json(msg)

        # We should not get execution reports for other orders
        client_order_id = msg.get("c")
        # assert client_order_id == order_id, f"Got event for wrong order, id {client_order_id}"

        if client_order_id == order_id:
            print("This message concerns our IOC order")

        print_colorful_json(msg)
        # done = True

    # Try to create 500 USD order that will get half filled
    market = "BTCUSDT"
    side = Side.ask
    info = get_depth_info(client, market, side)

    print("*** Order book status before meddling")
    print(f"Top {info.side.value} is {info.top_order_price} {info.quote_asset} with the quantity of {info.top_order_quantity} {info.base_asset}")
    print(f"Total {info.cumulative_depth} {info.base_asset} {info.side.value}s at the liquidity of {info.total_liquidity:,} {info.quote_asset}, average price is {info.avg_price} {info.quote_asset}")

    # Create a sell order we are later going to buy
    quantity = 0.005
    order = client.create_order(
        symbol=market,
        side=binance_enums.SIDE_SELL,
        type=binance_enums.ORDER_TYPE_LIMIT,
        timeInForce=binance_enums.TIME_IN_FORCE_GTC,
        quantity=str(quantity),
        price=str(info.top_order_price - 1))

    print("Our counter-sell order is", order)
    assert order["status"] == "NEW"

    info = get_depth_info(client, market, side)
    print("*** Order book after our test order injected")
    print(f"Top {info.side.value} is {info.top_order_price} {info.quote_asset} with the quantity of {info.top_order_quantity} {info.base_asset}")
    print(f"Total {info.cumulative_depth} {info.base_asset} {info.side.value}s at the liquidity of {info.total_liquidity:,} {info.quote_asset}, average price is {info.avg_price} {info.quote_asset}")

    if info.empty:
        sys.exit(f"There are no {info.side.value} orders available in the order book to test")

    if info.total_liquidity < 500:
        sys.exit(f"There is no liquidity available to perform the test")

    # Create a limit IOC order that cannot be fully filled
    quantity = 0.006
    order_start_price = info.top_order_price

    logger.info("Connecting to the websocket")
    bm.start()

    # start any sockets here, i.e a trade socket
    bm.start_user_socket(process_message)

    try:
        # https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md
        # IOC = Immediate or Cancel
        # try to fill as much as possible of the order before cancelling,
        # in this case we should get under 100% filled.
        # Also I can see that user socket receives no events about this order, only POST response
        # is given to the client - maybe I am doing it wrong.
        print(f"Creating buy limit order at {order_start_price} {info.quote_asset} for {quantity} {info.base_asset}")
        order_id = str(uuid.uuid4())
        order = client.create_order(
            newClientOrderId=order_id,
            symbol=market,
            side=binance_enums.SIDE_SELL if side == Side.bid else binance_enums.SIDE_BUY,
            type=binance_enums.ORDER_TYPE_LIMIT,
            timeInForce=binance_enums.TIME_IN_FORCE_IOC,
            quantity=str(quantity),
            price=str(order_start_price))

        print(f"Created order, data: {order}")

        # status is set to expired when we execute order only partially
        assert order["status"] == "EXPIRED"

        # We cannot fully execute (unless someone else is testing right now)
        assert float(order["executedQty"]) < float(order["origQty"])

        end_time = time.time() + 15
        while time.time() < end_time:
            print("Sill waiting", end_time - time.time(), "seconds")
            time.sleep(1.0)

    finally:
        print("Done, closing down might take a while")
        bm.stop()







