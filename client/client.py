import argparse
import time

from dht import DHT

# host1, port1 = 'localhost', 3001
# dht1 = DHT(host1, port1, regions[2])
#
# host2, port2 = 'localhost', 3002
# dht2 = DHT(host2, port2, regions[0])
#
# host3, port3 = 'localhost', 3003
# dht3 = DHT(host3, port3, regions[0])
#
# host4, port4 = 'localhost', 3004
# dht4 = DHT(host4, port4, regions[0])
#
# while not dht1.connected or not dht2.connected or not dht3.connected:
#     pass
#
# dht2["fungi"] = {'title': 'Fungi', 'type': 'Pica', 'description': 'Neki text', 'ingredients': ['Pencurke', 'Ono crveno', 'Sunka'], 'picture': 'neki base64 uzas djdhasdflkjashfkaskldfhas&^$^%GF*&^%R%RFG$RYF&%$'}
# dht2["kapricoza"] = {'title': 'Kapricoza', 'type': 'Pica', 'description': 'Neki text', 'ingredients': ['Pencurke', 'Ono crveno', 'Sunka'], 'picture': 'neki base64 uzas djdhasdflkjashfkaskldfhas&^$^%GF*&^%R%RFG$RYF&%$'}
# dht3["asd"] = {'title': 'Asd', 'type': 'Supa', 'description': 'ASDSPOAJDPOAJ', 'ingredients': ['Sarma'], 'picture': 'neki base64 uzas djdhasdflkjashfkaskldfhas&^$^%GF*&^%R%RFG$RYF&%$'}
#
# print dht1["Picafu"]
# print dht2["Supaasd"]
# print dht4["Pica"]


def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="Your IP address")
    parser.add_argument("port", help="Port to run dht on")
    parser.add_argument("region", help="Your region")
    args = parser.parse_args()

    dht = DHT(args.ip, int(args.port), args.region)

    while True:
        time.sleep(0.1)
        pass


if __name__ == '__main__':
    Main()
