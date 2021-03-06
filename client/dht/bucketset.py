import heapq
import threading
import sys

from .peer import Peer


def largest_differing_bit(value1, value2):
    distance = value1 ^ value2
    length = -1
    while (distance):
        distance >>= 1
        length += 1
    return max(0, length)


class BucketSet(object):
    def __init__(self, bucket_size, buckets, id):
        self.id = id
        self.bucket_size = bucket_size
        self.buckets = [list() for _ in range(buckets)]
        self.lock = threading.Lock()
        
    def insert(self, peer):
        if peer.id != self.id:
            bucket_number = largest_differing_bit(self.id, peer.id)
            peer_triple = peer.astriple()
            with self.lock:
                bucket = self.buckets[bucket_number]
                if peer_triple in bucket: 
                    bucket.pop(bucket.index(peer_triple))
                elif len(bucket) >= self.bucket_size:
                    prio = sys.maxint
                    tmp = None
                    for p_triple in bucket:
                        if p_triple[3] < prio:
                            tmp = p_triple
                            prio = p_triple[3]
                    bucket.pop(bucket.index(p_triple))
                bucket.append(peer_triple)
                
    def nearest_nodes(self, key, limit=None):
        num_results = limit if limit else self.bucket_size
        with self.lock:
            def keyfunction(peer):
                tmp = str(bin(key))
                if len(str(bin(key))) <= 257:
                    for i in range(len(str(bin(key))[:len(bin(key)) - 1]), 256):
                        tmp += '0'
                    return long(tmp, 2) ^ peer[2]
                else:
                    return key ^ peer[2]
            peers = (peer for bucket in self.buckets for peer in bucket)
            best_peers = heapq.nsmallest(num_results, peers, keyfunction)
            return [Peer(*peer) for peer in best_peers]

    def insert_list(self, peers):
        for peer in peers:
            self.insert(peer)

    def update_priority(self, message):
        with self.lock:
            for i in range(len(self.buckets)):
                for n in range(len(self.buckets[i])):
                    if self.buckets[i][n][2] == message["peer_id"]:
                        self.buckets[i][n] = (
                        self.buckets[i][n][0], self.buckets[i][n][1], self.buckets[i][n][2], self.buckets[i][n][3] + 1)
