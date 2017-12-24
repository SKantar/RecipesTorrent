for run in {1..10}
do
	port=$(($run+3100))
	python2 client.py 192.168.1.100 $port Daleko &
done
