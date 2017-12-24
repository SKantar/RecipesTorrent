import json
import random
import SocketServer
import time
import pickle

from .bucketset import *
from .hashing import hash_function, hash_function_partial
from .peer import Peer
from .shortlist import Shortlist
from config import *


class DHTRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        try:
            message = json.loads(self.request[0].strip())
            print "client: " + str(self.server.dht.peer.id) + " message: " + str(message)
            message_type = message["message_type"]
            if message_type == "ping":
                self.handle_ping(message)
            elif message_type == "pong":
                self.handle_pong(message)
            elif message_type == "oneup_category":
                self.handle_oneup_category(message)
            elif message_type == "find_node":
                self.handle_find(message)
            elif message_type == "find_value":
                self.handle_find(message, find_value=True)
            elif message_type == "find_category":
                self.handle_find_category(message)
            elif message_type == "found_category":
                self.handle_found_category(message)
            elif message_type == "found_nodes":
                self.handle_found_nodes(message)
            elif message_type == "found_value":
                self.handle_found_value(message)
            elif message_type == "store":
                self.handle_store(message)
            elif message_type == "bootstrap":
                self.handle_bootstrap(message)

            client_host, client_port = self.client_address
            peer_id = message["peer_id"]
            if peer_id != -1 and self.server.dht.buckets.id != -1:
                new_peer = Peer(unicode(client_host), client_port, peer_id)
                bucket_number = largest_differing_bit(self.server.dht.buckets.id, new_peer.id)
                if len(self.server.dht.buckets.buckets[bucket_number]) < k:
                    self.server.dht.buckets.insert(new_peer)
        except KeyError:
            pass

    def handle_ping(self, message):
        client_host, client_port = self.client_address
        id = message["peer_id"]
        peer = Peer(client_host, client_port, id)
        peer.pong(socket=self.server.socket, peer_id=self.server.dht.peer.id, lock=self.server.send_lock)
        
    def handle_pong(self, message):
        pass

    def handle_oneup_category(self, message):
        self.server.dht.categories[message["category"]] += 1

    def handle_find_category(self, message):
        key = message["id"]
        key_full = message["id_full"]
        id = message["peer_id"]
        client_host, client_port = self.client_address
        peer = Peer(client_host, client_port, id)
        response_socket = self.request[1]
        values = {}
        if key_full in self.server.dht.data:
            peer.found_value(id, self.server.dht.data[key_full], message["rpc_id"], socket=response_socket, peer_id=self.server.dht.peer.id, lock=self.server.send_lock)
            return
        for t in self.server.dht.data:
            if str(bin(t)).startswith(str(bin(key))):
                values[t] = self.server.dht.data[t]

        nodes = self.server.dht.buckets.nearest_nodes(key)
        nearest_nodes = [nearest_peer.astriple() for nearest_peer in nodes]

        value = {"values": values, "nodes": nearest_nodes}
        peer.found_category(id, value, message["rpc_id"], socket=response_socket, peer_id=self.server.dht.peer.id, lock=self.server.send_lock)

    def handle_found_category(self, message):
        rpc_id = message["rpc_id"]
        shortlist = self.server.dht.rpc_ids[rpc_id]
        del self.server.dht.rpc_ids[rpc_id]
        nearest_nodes = [Peer(*peer) for peer in message["nodes"]]
        shortlist.update(nearest_nodes)
        for key in message["values"]:
            hashed_key = hash_function(message["values"][key]["type"], message["values"][key]["title"])
            self.server.dht.data[hashed_key] = message['values'][key]
            if self.server.dht.storage:
                output = open("%s/%s.pkl" % (self.server.dht.storage, hashed_key), 'wb')
                pickle.dump(message["values"][key], output)
                output.close()
            self.server.dht[message['values'][key]['title']] = message["values"][key]
            if not shortlist.category:
                shortlist.category = message["values"][key]["type"]

    def handle_find(self, message, find_value=False):
        key = message["id"]
        id = message["peer_id"]
        client_host, client_port = self.client_address
        peer = Peer(client_host, client_port, id)
        response_socket = self.request[1]
        value = None
        if find_value:
            for t in self.server.dht.data:
                if str(bin(t)).endswith(str(bin(key))[2:]):
                    value = self.server.dht.data[t]
                    break
        if find_value and value:
            peer.found_value(id, value, message["rpc_id"], socket=response_socket, peer_id=self.server.dht.peer.id, lock=self.server.send_lock)
        else:
            nearest_nodes = self.server.dht.buckets.nearest_nodes(id)
            if not nearest_nodes:
                nearest_nodes.append(self.server.dht.peer)
            nearest_nodes = [nearest_peer.astriple() for nearest_peer in nearest_nodes]
            peer.found_nodes(id, nearest_nodes, message["rpc_id"], socket=response_socket, peer_id=self.server.dht.peer.id, lock=self.server.send_lock)

    def handle_found_nodes(self, message):
        rpc_id = message["rpc_id"]
        shortlist = self.server.dht.rpc_ids[rpc_id]
        del self.server.dht.rpc_ids[rpc_id]
        nearest_nodes = [Peer(*peer) for peer in message["nearest_nodes"]]
        shortlist.update(nearest_nodes)

    def handle_found_value(self, message):
        rpc_id = message["rpc_id"]
        shortlist = self.server.dht.rpc_ids[rpc_id]
        del self.server.dht.rpc_ids[rpc_id]
        shortlist.set_complete(message["value"])
        shortlist.category = message["type"]
        key = hash_function(message["value"]["type"], message["value"]["title"])
        self.server.dht.data[key] = message['value']
        if self.server.dht.storage:
            output = open("%s/%s.pkl" % (self.server.dht.storage, key), 'wb')
            pickle.dump(message["value"], output)
            output.close()
        if self.from_popular_category(message["type"]):
            self.server.dht.buckets.update_priority(message)

    def from_popular_category(self, type):
        n = 0
        for cat in self.server.dht.categories:
            n += self.server.dht.categories[cat]
        x = self.server.dht.categories[type]
        if n * popular_threshold <= x:
            return True
        return False

    def handle_store(self, message):
        #print message
        key = message["id"]
        if key not in self.server.dht.data:
            self.server.dht.data[key] = message["value"]
            if self.server.dht.storage:
                output = open("%s/%s.pkl" % (self.server.dht.storage, key), 'wb')
                pickle.dump(message["value"], output)
                output.close()

    def handle_bootstrap(self, message):
        unique_id = message["value"][0]
        if self.server.dht.id == -1:
            self.server.dht.peer.id = unique_id
            self.server.dht.buckets.id = unique_id
        print self.server.dht.peer
        if message["value"][1] is not None:
            print "\tboot_host:" + str(message["value"][1])
            print "\tboot_port:" + str(message["value"][2])
            print "\tboot_id:" + str(message["value"][3])
            boot_peer = Peer(unicode(message["value"][1]), message["value"][2], message["value"][3])
            self.server.dht.connect(boot_peer)
        else:
            self.server.dht.connected = True


class DHTServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    def __init__(self, host_address, handler_cls):
        SocketServer.UDPServer.allow_reuse_address = True
        SocketServer.UDPServer.__init__(self, host_address, handler_cls)
        self.send_lock = threading.Lock()


class DHT(object):
    def __init__(self, host, port, region, id=-1, storage=None):
        self.categories = {}
        self.id = id
        for category in category_names:
            self.categories[category] = 0
        self.connected = False
        self.storage = storage
        self.peer = Peer(unicode(host), port, self.id)
        self.data = {}
        self.buckets = BucketSet(k, id_bits, self.peer.id)
        self.rpc_ids = {}
        self.server = DHTServer(self.peer.address(), DHTRequestHandler)
        self.server.dht = self
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        bootstrap_server = Peer(unicode(BOOTSTRAP_HOST), BOOTSTRAP_PORT, -1)
        # Stavio sam -1 i 0 posto ovi parametri se ne koriste u handle_find KOD BOOTSTRAP-A
        bootstrap_server.bootstrap(region, socket=self.server.socket, peer_id=-1)

    def iterative_find_nodes(self, key, boot_peer=None):
        shortlist = Shortlist(k, key)
        shortlist.update(self.buckets.nearest_nodes(key, limit=alpha))
        if boot_peer:
            rpc_id = random.getrandbits(id_bits)
            self.rpc_ids[rpc_id] = shortlist
            boot_peer.find_node(key, rpc_id, socket=self.server.socket, peer_id=self.peer.id)
        while (not shortlist.complete()) or boot_peer:
            nearest_nodes = shortlist.get_next_iteration(alpha)
            for peer in nearest_nodes:
                shortlist.mark(peer)
                rpc_id = random.getrandbits(id_bits)
                self.rpc_ids[rpc_id] = shortlist
                peer.find_node(key, rpc_id, socket=self.server.socket, peer_id=self.peer.id)
            time.sleep(iteration_sleep)
            boot_peer = None
        return shortlist.results()

    def iterative_find_category(self, key, key_full):
        shortlist = Shortlist(k, key)
        shortlist.update(self.buckets.nearest_nodes(key, limit=alpha))
        while not shortlist.complete():
            nearest_nodes = shortlist.get_next_iteration(alpha)
            for peer in nearest_nodes:
                shortlist.mark(peer)
                rpc_id = random.getrandbits(id_bits)
                self.rpc_ids[rpc_id] = shortlist
                peer.find_category(key, key_full, rpc_id, socket=self.server.socket, peer_id=self.peer.id)
            time.sleep(iteration_sleep)
        while not shortlist.category:
            pass
        threading.Thread(target=self.oneup_category, args=(shortlist.category, None)).start()

    def oneup_category(self, category, nesto):
        self.categories[category] += 1
        for i in range(224):
            for peer in self.buckets.buckets[i]:
                Peer(*peer).oneup_category(category, socket=self.server.socket, peer_id=self.peer.id, lock=self.server.send_lock)
                time.sleep(0.2)

    def iterative_find_value(self, key):
        shortlist = Shortlist(k, key)
        shortlist.update(self.buckets.nearest_nodes(key, limit=alpha))
        while not shortlist.complete():
            nearest_nodes = shortlist.get_next_iteration(alpha)
            for peer in nearest_nodes:
                shortlist.mark(peer)
                rpc_id = random.getrandbits(id_bits)
                self.rpc_ids[rpc_id] = shortlist
                peer.find_value(key, rpc_id, socket=self.server.socket, peer_id=self.peer.id)
            time.sleep(iteration_sleep)
        return shortlist.completion_result()
            
    def connect(self, boot_peer):
        self.buckets.insert_list(self.iterative_find_nodes(self.peer.id, boot_peer=boot_peer))
        self.connected = True
                    
    def __getitem__(self, key):
        hashed_key, hashed_key_full, n = hash_function_partial(key)
        if hashed_key_full in self.data:
            return self.data[hashed_key_full]
        threading.Thread(target=self.iterative_find_category, args=(hashed_key, hashed_key_full)).start()
        return None

        # if key in self.server.dht.categories:
        #
        #     self.server.dht.categories[key] += 1
        #     threading.Thread(self.iterative_find_category(hashed_key)).start()
        # else:
        #     hashed_key = hash_function(None, key)
        #     for t in self.data:
        #         if str(bin(t)).endswith(str(bin(hashed_key))[2:]):
        #             return self.data[t]
        #     result = self.iterative_find_value(hashed_key)
        #     if result:
        #         self.__setitem__(key, result)
        #         return result
        # return None
        
    def __setitem__(self, key, value):
        hashed_key = hash_function(value["type"], key)
        nearest_nodes = self.iterative_find_nodes(hashed_key)
        self.data[hashed_key] = value

        if self.storage:
            output = open("%s/%s.pkl" % (self.storage, hashed_key), 'wb')
            pickle.dump(value, output)
            output.close()

        for node in nearest_nodes:
            node.store(hashed_key, value, socket=self.server.socket, peer_id=self.peer.id)
        
    def tick(self):
        pass
