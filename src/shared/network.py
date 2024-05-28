from threading import Lock, Thread
from queue import Queue, Empty
from shared.time import Time, get_time, add_seconds
from shared.threading import Atom

type IpV4 = int
"""Time of arrival and message, internal type"""
type Packet[Message] = tuple[Time, Message]
"""Time of arrival and message"""
type Arrived[Message] = tuple[Time, Message]


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
        self._clients[ip].put((t_arrive, msg))

    def receive(self, ip: IpV4) -> list[Arrived[Message]]:
        """receive a list of messages for this ip, sorted oldest first"""
        self.add_client_if_missing(ip)
        t = get_time()
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
        return sorted(arrived, key=lambda _: _[0])


class Receiver[Message]:
    """Receiver is running constantly in seperate thread

    Enables messages to be tagged with exact time of arrival
    """

    _network: Network[Message]
    _ip: IpV4
    _received: Queue[Arrived[Message]] = Queue()
    _deleted: Atom[bool] = Atom(False)

    def __init__(self, network: Network[Message], ip: IpV4) -> None:
        self._network = network
        self._ip = ip
        Thread(target=self._receive_loop, args=()).start()

    def __del__(self) -> None:
        self._deleted.set(True)

    def received(self) -> list[Arrived[Message]]:
        """Get all messages arrived since last call"""
        received = list[Arrived[Message]]()
        while True:
            try:
                received.append(self._received.get_nowait())
            except Empty:
                break
        return sorted(received, key=lambda _: _[0])

    def received_until(self, t: Time) -> list[Arrived[Message]]:
        """Get all messages arrived between last requested time and t"""
        received = list[Arrived[Message]]()
        not_received = list[Arrived[Message]]()
        while True:
            try:
                msg = self._received.get_nowait()
                if msg[0] > t:
                    not_received.append(msg)
                else:
                    received.append(msg)
            except Empty:
                break
        for msg in not_received:
            self._received.put(msg)
        return sorted(received, key=lambda _: _[0])

    def _receive_loop(self):
        """[internal] receive messages and tag with exact receive time"""
        while not self._deleted.get():
            messages = self._network.receive(self._ip)
            for msg in messages:
                self._received.put(msg)
