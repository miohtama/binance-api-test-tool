"""Binance API test tool.

Make a marker order on Binance Spot Testnet to move the market.

This is to trigger your own limit orders and then your client to get event for the triggered orders.
Needed for manual simulation of different event flows or integration testing.

Tutorials:

- https://dev.to/drcloudycoder/develop-python-cli-with-subcommands-using-click-4892

"""

import logging
from decimal import Decimal
from dataclasses import dataclass
from functools import partial
from inspect import getmembers, isfunction
import os
import sys

import click
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance_testnet_tool.logs import setup_logging
from binance_testnet_tool.console import print_colorful_json
from binance_testnet_tool.utils import quantize_price
from binance_testnet_tool.utils import quantize_quantity
from binance_testnet_tool.requesthelpers import hook_request_dump
from binance import enums as binance_enums
from pycoingecko import CoinGeckoAPI
from dotenv import load_dotenv
from tabulate import tabulate


logger = logging.getLogger()

client: Client = None

bm: BinanceSocketManager = None

# https://github.com/pallets/click/issues/646#issuecomment-435317967
click.option = partial(click.option, show_default=True)


@dataclass
class BinanceUrlConfig:
    """URLS for Binance API interaction.

    Lose your money and Spot Testnet flavours.

    Looks like python-binance does not have direct support for Spot Testnet urls.
    """

    api_end_point: str
    stream_url: str

    def __init__(self, network: str):
        if network == "spot-testnet":
            self.api_end_point = "https://testnet.binance.vision/api"
            # self.user_stream_endpoint = "userDataStream"
            self.stream_url = "wss://testnet.binance.vision/ws/"
        elif network == "production":
            self.api_end_point = Client.API_URL
            # self.user_stream_endpoint = "userDataStream"
            self.stream_url = "wss://stream.binance.{}:9443/ws/"
        else:
            raise RuntimeError(f"Unknown Binance network {network}")


def create_client(api_key, api_secret, network: str):
    """Create Binance client with proper testnet configuration."""

    if not network:
        network = os.environ.get("BINANCE_NETWORK")

    assert network, "You need to choose Binance API network"

    # Patch the client for testnet if needed
    urls = BinanceUrlConfig(network)
    Client.API_URL = urls.api_end_point

    if not api_key:
        api_key = os.environ.get("BINANCE_API_KEY")

    if not api_secret:
        api_secret = os.environ.get("BINANCE_API_SECRET")

    client = Client(api_key=api_key, api_secret=api_secret)

    # Add our HTTP POST debug dumper
    client.session.hooks["response"].append(hook_request_dump)

    bm = BinanceSocketManager(client)
    bm.STREAM_URL = urls.stream_url

    logger.info("Binance client configured for %s", network)
    logger.info("API key: %s", client.API_KEY)
    logger.info("Using HTTP API endpoint: %s", client.API_URL)
    logger.info("Using WebSocket API endpoint: %s", bm.STREAM_URL)

    if not client.API_KEY:
        logger.warning("Binance API key not configured, only public API functions available")

    return client, bm


def check_accounted_api_client():
    """Raises an error if we do not have an API key configured."""
    if not client.API_KEY:
        raise RuntimeError("To call this command you need to have your Binance API key configured")


@click.command()
@click.option('--market', default="BTCUSDT", help='Market where the order is made', required=True)
@click.option('--side', help='Are you buying or selling', type=click.Choice(['buy', 'sell']), required=True)
@click.option('--quantity', default="0.01", help='Amount of base pair is being traded (e.g. BTC)', required=True, type=float)
@click.option('--price-amount', default=None, help='Set price as quote pair (e.g. in Dollar)', required=False, type=float)
@click.option('--price-percent', default=None, help='Set price as a +/- % to reference price based on Coingecko', required=False, type=float)
def create_limit_order(market: str, side: str, quantity: float, price_amount: float, price_percent: float):
    """Add liquidity to the market.

    Show the Binance order execution results.
    Limit orders can be immediately executed (reflected in the result) or left open.
    """

    check_accounted_api_client()

    if not any([price_amount, price_percent]):
        raise RuntimeError("You need to give a percent price or absolute price.")

    if price_amount:
        price = Decimal(price_amount)
    else:
        assert market == "BTCUSDT", "No other markets supported at the yet"
        cg = CoinGeckoAPI()
        data = cg.get_price(ids='bitcoin', vs_currencies='usd')
        price = Decimal(data["bitcoin"]["usd"])

        assert price_percent > -100
        assert price_percent < 100

        price *= Decimal(1) + Decimal(price_percent / 100.0)

    # Always use decimals and present prices up a certain decimal
    price = quantize_price(price)
    quantity = quantize_quantity(quantity)

    logger.info("Creating a %s limit order for %s, at %f for %f crypto", side, market, price, quantity)

    order = client.create_order(
        symbol=market,
        side=binance_enums.SIDE_BUY if side == "buy" else binance_enums.SIDE_SELL,
        type=binance_enums.ORDER_TYPE_LIMIT,
        timeInForce=binance_enums.TIME_IN_FORCE_GTC,
        quantity=str(quantity),
        price=str(price))

    logger.info("Order created")
    print_colorful_json(order)


@click.command()
@click.option('--market', default="BTCUSDT", help='Market where the order is made', required=True)
@click.option('--side', help='Are you buying or selling', type=click.Choice(['buy', 'sell']), required=True)
@click.option('--quantity', default="0.001", help='Amount of base pair is being traded (e.g. BTC)', required=True, type=float)
def create_market_order(market: str, side: str, quantity: float):
    """Move the market.

    Binance markets orders do not have price.
    """

    check_accounted_api_client()

    quantity = quantize_quantity(quantity)

    logger.info("Creating a %s market order for %s, for %f crypto", side, market, quantity)
    order = client.create_order(
        symbol=market,
        side=binance_enums.SIDE_BUY if side == "buy" else binance_enums.SIDE_SELL,
        type=binance_enums.ORDER_TYPE_MARKET,
        quantity=str(quantity))
    logger.info("Order created")
    print_colorful_json(order)

    if order["executedQty"] != order["origQty"]:
        logger.warning("Could not fill the order, executed only %s", order["executedQty"])


@click.command()
def status():
    """Print exchange status"""
    status = client.get_system_status()
    print(f"The status of {client.API_URL} is: {status['msg']}")


@click.command()
def available_markets():
    """Available pairs for the user to trade"""
    tokens = client.get_all_tickers()
    tokens = sorted(tokens, key=lambda x: x["symbol"])

    def get_entries():
        entries = []
        for idx, token in enumerate(tokens):
            yield idx + 1, token["symbol"], token["price"]

    headers = ["#", "Symbol", "Midprice"]
    print(tabulate(get_entries(), headers, floatfmt=".8f"))


@click.command()
@click.option('--market', default="BTCUSDT", help='Which market', required=True)
def market_info(market: str):
    """Information on a single trading pair"""
    info = client.get_symbol_info(market)
    print_colorful_json(info)


@click.command()
@click.option('--market', default="BTCUSDT", help='Which market', required=True)
def current_price(market: str):
    """Current price info for a trading pair"""
    depth = client.get_order_book(symbol=market)
    avg = client.get_avg_price(symbol=market)

    print("Pair", market)
    print("Mid price:", avg["price"], "for the period of", avg["mins"], "minutes")
    asks = sorted(depth["asks"], key=lambda x: float(x[0]))
    if asks:
        top_ask, top_ask_quantity = asks[0]
        top_ask = float(top_ask)
        print("Ask top (most money you can make by buying):", top_ask)
    else:
        top_ask = None
        print("No asks (nobody is selling)")

    bids = sorted(depth["bids"], key=lambda x: -float(x[0]))
    if bids:
        top_bid, top_bid_quantity = bids[0]
        top_bid = float(top_bid)
        print("Bid top (most money you can make by selling):", top_bid)
    else:
        top_bid = None
        print("No bids (nobody is buying)")

    if top_ask and top_bid:
        print("Spread", 100 * (top_ask - top_bid) / top_bid, "%")


@click.command()
@click.option('--market', default="BTCUSDT", help='Which market', required=True)
def depth(market: str):
    """Show orderbook depth"""

    depth = client.get_order_book(symbol=market)

    print("Pair", market)
    asks = sorted(depth["asks"], key=lambda x: float(x[0]))
    bids = sorted(depth["bids"], key=lambda x: -float(x[0]))

    if not asks:
        print("Order book has no asks - cannot market buy")
    else:
        top_ask, top_ask_quantity = asks[0]
        top_ask = float(top_ask)
        print("Top ask is", top_ask, "with the quantity of", top_ask_quantity)
        cumulative_depth = total_liquidity = 0
        for price, quantity in asks:
            price = float(price)
            quantity = float(quantity)
            total_liquidity += price * quantity
            cumulative_depth += quantity
        avg_price = total_liquidity / cumulative_depth
        print(f"Total {cumulative_depth} asks at the liquidity of {total_liquidity:,}, average price is {avg_price}")

    if not bids:
        print("Order book has no bids - cannot market sell")
    else:
        top_bid, top_bid_quantity = bids[0]
        top_bid = float(top_bid)
        print("Top bid is", top_bid, "with the quantity of", top_bid_quantity)
        cumulative_depth = total_liquidity = 0
        for price, quantity in bids:
            price = float(price)
            quantity = float(quantity)
            total_liquidity += price * quantity
            cumulative_depth += quantity
        avg_price = total_liquidity / cumulative_depth
        print(f"Total {cumulative_depth} bids at the liquidity of {total_liquidity:,}, average price is {avg_price}")


@click.command()
def balances():
    """Account balances"""

    check_accounted_api_client()

    tokens = client.get_account()["balances"]
    tokens = sorted(tokens, key=lambda x: x["asset"])

    def get_entries():
        entries = []
        for idx, token in enumerate(tokens):
            yield idx + 1, token["asset"], token["free"], token["locked"]

    headers = ["#", "Symbol", "Free balance", "Locked balance"]
    print(tabulate(get_entries(), headers, floatfmt=".8f"))


@click.command()
def orders():
    """Open orders"""

    check_accounted_api_client()

    orders = client.get_open_orders()
    orders = sorted(orders, key=lambda x: x["orderId"])
    def get_entries():
        entries = []
        for order in orders:
            yield order["orderId"], order["symbol"], order["type"], order["side"], order["status"], order["price"], order["origQty"], order["executedQty"]

    headers = ["Order id", "Market", "Type", "Side", "Status", "Price", "Quantity quoted", "Quantity executed"]
    print(tabulate(get_entries(), headers, floatfmt=".8f"))


@click.command()
@click.option('--market', default="BTCUSDT", help='Which market', required=True)
@click.option('--order-id', help='Binance order id', required=True)
def check_order(market: str, order_id: str):
    """Status of a single order"""

    check_accounted_api_client()
    order_data = client.get_order(symbol=market, orderId=order_id)
    print_colorful_json(order_data)


@click.command()
def cancel_all():
    """Cancel all open orders"""

    check_accounted_api_client()

    orders = client.get_open_orders()

    if len(orders) == 0:
        print("No open orders to cancel")

    for o in orders:
        logger.info("Cancelling order %s", o["orderId"])
        client.cancel_order(symbol=o["symbol"], orderId=o["orderId"])


@click.command()
def order_event_stream():
    """Open order event stream"""

    check_accounted_api_client()

    def process_message(msg: dict):
        logger.info("Received event %s", msg["e"])
        print_colorful_json(msg)

    logger.info("Connecting to the websocket")

    # start any sockets here, i.e a trade socket
    conn_key = bm.start_user_socket(process_message)
    # then start the socket manager

    logger.info("Connected - stream running - do some orders in another terminal")
    bm.start()


@click.command()
def version():
    """Print version to stdout and exit"""
    import binance_testnet_tool
    print(binance_testnet_tool.__version__)


@click.command()
def console():
    """Interactive IPython console session"""

    # https://ipython.readthedocs.io/en/stable/interactive/reference.html#embedding
    imported_objects = {}
    import datetime
    from IPython import embed

    # Import some generic commands
    imported_objects["client"] = client
    imported_objects["bm"] = bm
    imported_objects["binance_enums"] = binance_enums
    imported_objects["datetime"] = datetime
    imported_objects["tabulate"] = tabulate
    imported_objects["print_colorful_json"] = print_colorful_json

    # Patch some missing help texts
    client.__doc__ = "Binance client"
    bm.__doc__ = "Binance WebSockets manager"
    binance_enums.__doc__ = "Binance API enums"

    def _call_click_command(cmd: click.Command, *args, **kwargs):
        result = cmd.callback(*args, **kwargs)
        return result

    # Pull out all Click commands from the current module
    module = sys.modules[__name__]
    for name, obj in getmembers(module):
        if isinstance(obj, click.Command) and not isinstance(obj, click.Group):
            # Create a wrapper Python function that calls click Command.
            # We also set docstring of this function correctly.
            name = name.replace("-", "_")
            func = partial(_call_click_command, obj)
            func.__doc__ = obj.__doc__
            imported_objects[name] = func

    print('')
    print('Following objects and functions are available in Python session:')

    def get_entries():
        entries = []
        for key, obj in imported_objects.items():
            key = key.replace("-", "_")
            help = ""
            doc = getattr(obj, "__doc__", None)
            if doc:
                help = doc.split("\n")[0]
            yield key, help, str(obj)[0:40],

    headers = ["Name", "Help", "Object"]
    print(tabulate(get_entries(), headers))
    print('')

    embed(user_ns=imported_objects, colors="Linux")


@click.group("Binance API Tester command line tool")
@click.option('--api-key', default=None, help='Binance API key', required=False)
@click.option('--api-secret', default=None, help='Binance API secret', required=False)
@click.option('--log-level', default="info", help='Python logging level', required=False)
@click.option('--config-file', default=None, help='Read environment variables from this INI config file', required=False, type=click.Path(exists=True))
@click.option('--network',  help='Binance API endpoint to use', type=click.Choice(['production', 'spot-testnet']), required=False)
def main(api_key, api_secret, network, log_level, config_file):
    global client
    global bm
    setup_logging(log_level)

    # Read the configuratation
    if config_file:
        load_dotenv(dotenv_path=config_file, verbose=True)
        logger.info("Loaded API keys from %s", config_file)

    client, bm = create_client(api_key, api_secret, network)
    # Here jumps to the subcommand by click


main.add_command(status)
main.add_command(available_markets)
main.add_command(market_info)
main.add_command(create_limit_order)
main.add_command(create_market_order)
main.add_command(current_price)
main.add_command(depth)
main.add_command(balances)
main.add_command(orders)
main.add_command(check_order)
main.add_command(cancel_all)
main.add_command(order_event_stream)
main.add_command(version)
main.add_command(console)


if __name__ == "__main__":
    main()
