import argparse
import logging
from threading import Thread

from roboarena.client.client import Client
from roboarena.server.server import Server
from roboarena.shared.constants import SERVER_IP
from roboarena.shared.network import Network
from roboarena.shared.types import EventType

""" Command line argument parsing
"""

arg_parser = argparse.ArgumentParser(
    prog="Robo-Arena",
    description="An rogue-like with an infinite map, isn't it cool?",
)
arg_parser.add_argument(
    "-ll",
    "--loglevel",
    nargs="?",
    default="warning",
    choices=["debug", "info", "warning", "error", "critical"],
)
arg_parser.add_argument("-lf", "--logfile", nargs=1)
args = arg_parser.parse_args()

""" Logging
"""

loglevel = args.loglevel.upper()
if args.logfile:
    logging.basicConfig(filename=args.logfile, level=loglevel)
else:
    logging.basicConfig(level=loglevel)
logger = logging.getLogger(__name__)

network = Network[EventType](0)
logger.info("initialized network")

server = Server(network, SERVER_IP)
Thread(target=lambda: server.loop()).start()
logger.info("started server")

client = Client(network, 0x00000001)
client.loop()
