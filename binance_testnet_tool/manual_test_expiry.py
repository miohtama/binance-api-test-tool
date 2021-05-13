"""Test expiring orders on the spot testnest"""

import click
from binance_testnet_tool.logs import setup_logging
from binance_testnet_tool.main import create_client
from binance_testnet_tool.main import check_accounted_api_client
from binance_testnet_tool.console import print_colorful_json
from dotenv import load_dotenv

logger = logging.getLogger()

# Start listetning incoming orders
@click.group("Binance order book event expiry test")
@click.option('--api-key', default=None, help='Binance API key', required=False)
@click.option('--api-secret', default=None, help='Binance API secret', required=False)
@click.option('--log-level', default="info", help='Python logging level', required=False)
@click.option('--config-file', default=None, help='Read environment variables from this INI config file', required=False, type=click.Path(exists=True))
def main(api_key, api_secret, network, log_level, config_file):
    global client
    global bm

    setup_logging(log_level)

    # Read the configuratation
    if config_file:
        load_dotenv(dotenv_path=config_file, verbose=True)
        logger.info("Loaded API keys from %s", config_file)

    order_book = "BTCUSD"
    network = "spot-testnet"

    client, bm = create_client(api_key, api_secret, network)

    # Subscribe to the events
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



