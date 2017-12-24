import random
import SocketServer
import threading

from client.dht.config import *
from client.dht.peer import *


class BootstrapRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            message = json.loads(self.request[0].strip())
            message_type = message["message_type"]
            if message_type == "pong":
                self.handle_pong(message)
            elif message_type == "bootstrap":
                self.handle_bootstrap(message)

        except KeyError, ValueError:
            pass

    def handle_pong(self, message):
        pass

    def handle_bootstrap(self, message):
        print "New peer connecting"

        region = message["value"]
        print "\tRegion: " + region

        client_host, client_port = self.client_address

        region_index = regions.index(region)
        region_id = (1 << region_index) << 224
        unique_id = self.server.dht.next_id

        print "\tRegion Id (Bin):" + "{0:b}".format(region_id)
        print "\tUnique Id (Dec):" + str(unique_id)

        peer = Peer(unicode(client_host), client_port, region_id + unique_id)
        print "\tAddress:" + str(peer.address())
        peers = self.server.dht.peers
        random_node_host = None
        random_node_port = None
        random_node_id = None

        print "\tPeers Length:" + str(len(peers))
        index = -1
        for i, p in enumerate(peers):
            if peer.address() == p.address():
                index = i
                break
        if index != -1:
            del self.server.dht.peers[index]

        state = random.getstate()
        random.seed(BOOTSTRAP_SEED)
        if len(peers) > 0:
            while random_node_host is None:
                random_node_index = random.randint(0, len(peers) - 1)
                random_node_host = peers[random_node_index].host
                random_node_port = peers[random_node_index].port
                random_node_id = peers[random_node_index].id
        random.setstate(state)

        if len(peers) >= 20:
            self.server.dht.peers.pop(0)
        self.server.dht.peers.append(peer)

        self.server.dht.next_id += 1
        if self.server.dht.next_id >= 2**224 - 1:
            self.server.dht.next_id = 0
        response_socket = self.request[1]
        peer.bootstrap(value=(region_id + unique_id, random_node_host, random_node_port, random_node_id), socket=response_socket, peer_id=-1)


class BootstrapServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    def __init__(self, host_address, handler_cls):
        SocketServer.UDPServer.__init__(self, host_address, handler_cls)
        self.send_lock = threading.Lock()


class Bootstrap:
    def __init__(self):
        self.peers = []
        self.rpc_ids = {}
        self.server = BootstrapServer(("", BOOTSTRAP_PORT), BootstrapRequestHandler)
        self.server.dht = self
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.next_id = 0


if __name__ == "__main__":
    Bootstrap()
    print "Bootstrap is running"
    while 1:
        pass
