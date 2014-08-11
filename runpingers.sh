#!/bin/sh

BRIDGE=br-em1
BASEADDR=192.168.1.170
NETMASK=24
PIPEWORK=$HOME/bin/pipework

etcd=$(docker run -d --name etcd coreos/etcd || echo FAIL)
if [ "$etcd" = "FAIL" ]; then
	echo "failed to start etcd container" >&2
	exit 1
fi
echo "etcd container is $etcd"

pingers=()
base_prefix=${BASEADDR%.*}
base_suffix=${BASEADDR##*.}

for x in {0..3}; do
	pingers[$x]=$(docker run -d --link etcd:etcd --name pinger$x pinger)
	pingerip="${base_prefix}.$(( $base_suffix + $x ))"
	echo "pinger $x is ${pingers[$x]} @ $pingerip"
	sleep 1
	sudo $PIPEWORK $BRIDGE ${pingers[$x]} $pingerip/$NETMASK
done

echo "press RETURN to stop and remove containers"
read junk

for pinger in ${pingers[@]}; do
	docker rm -f $pinger
done

docker rm -f $etcd

