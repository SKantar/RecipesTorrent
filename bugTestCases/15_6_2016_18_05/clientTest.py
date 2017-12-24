from dht import DHT
import dht.config
import random
import time

# Stavite da je config.k = 2 (ili 3) ako je vece, bice potpun graf jer je malo cvorova

DHT_NUM = 8
RECEPTI_NUM = 5


state = random.getstate()
random.seed(dht.config.TESTING_CATEGORY_SEED)
recepti = [{
    'title': 'naziv' + str(i),
    'type': dht.config.category_names[random.randint(0, len(dht.config.category_names) - 1)],
    'description': 'Opis ' + str(i),
    'ingredients': ['Sastojak_1_' + str(i), 'Sastojak_2_' + str(i), 'Sastojak_3_' + str(i)],
    'picture': None
} for i in range(RECEPTI_NUM)]
random.setstate(state)

dht = [DHT("localhost", 3001 + i, dht.config.regions[i % len(dht.config.regions)]) for i in range(DHT_NUM)]

# Sacekaj dok se svi konektuju
all_connected = False
while not all_connected:
    all_connected = True
    for d in dht:
        if not d.connected:
            all_connected = False
            break

print "KONEKCIJE"
for d in dht:
    print d.peer.address()
    peer_sum = 0
    for b_index, bucket in enumerate(d.buckets.buckets):
        for peer in bucket:
            peer_sum += 1
            print "\t" + str(peer_sum) + " Bucket " + str(b_index) + " " + str(peer)

dht[2]["naziv2"] = recepti[2] # Host na 3003

print "Search 1"
print dht[0][recepti[2]['type'] + "naz"] # Host na 3001
time.sleep(5)
print "Search 2"
print dht[0][recepti[2]['type'] + "naziv2"] # Host na 3001

while True:
    pass

