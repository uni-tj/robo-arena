import logging
from collections.abc import Iterable
from queue import Empty, Queue
from threading import Lock
from typing import Optional

from roboarena.shared.time import add_seconds, get_time
from roboarena.shared.types import Arrived, IpV4, Packet, Time

logger = logging.getLogger(__name__)


class Network[Message]:
    """Thread-safe Network emulator"""

    _add_client_lock: Lock = Lock()
    _clients: dict[IpV4, Queue[Packet[Message]]] = {}
    _delay: float

    def __init__(self, delay: float) -> None:
        self._delay = delay

    def add_client_if_missing(self, ip: IpV4):
        with Network._add_client_lock:
            if ip not in self._clients:
                self._clients[ip] = Queue()

    def send(self, ip: IpV4, msg: Message):
        self.add_client_if_missing(ip)
        t_arrive = add_seconds(get_time(), self._delay)
        # logger.debug(f"sending message {(t_arrive, msg)}")
        self._clients[ip].put((t_arrive, msg))

    def receive(
        self, ip: IpV4, *, until: Optional[Time] = None
    ) -> list[Arrived[Message]]:
        """receive a list of messages for this ip, sorted oldest first"""
        self.add_client_if_missing(ip)
        t = until or get_time()
        arrived = list[Packet[Message]]()
        not_arrived = list[Packet[Message]]()
        while True:
            try:
                packet = self._clients[ip].get_nowait()
                t_arrive, _ = packet
                if t_arrive > t:
                    not_arrived.append(packet)
                else:
                    arrived.append(packet)
            except Empty:
                break
        for packet in not_arrived:
            self._clients[ip].put(packet)

        # for t_arrive, msg in sorted(arrived, key=lambda _: _[0]):
        #     logger.debug(f"receiving message {(t_arrive, msg)}")
        return sorted(arrived, key=lambda _: _[0])

    def receive_one(self, ip: IpV4) -> None | Arrived[Message]:
        """receive the oldest message for this ip"""
        arrived = self.receive(ip)
        if len(arrived) == 0:
            return None
        oldest, *other = arrived
        for packet in other:
            self._clients[ip].put(packet)
        return oldest


class Receiver[T]:
    _network: Network[T]
    _ip: IpV4
    _received: Iterable[Arrived[T]]

    def __init__(self, network: Network[T], ip: IpV4) -> None:
        self._network = network
        self._ip = ip
        self._received = list()

    def receive(self, *, until: Optional[Time] = None) -> list[Arrived[T]]:
        return self._network.receive(self._ip, until=until)
