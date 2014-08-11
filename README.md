This was inspired by a conversation on IRC in `#docker`.

The goal is to create *N* containers, each with an interface on a
local L2 network.  The containers should boot up start generating
traffic among all available containers.

For connectivity to the local L2 network, we assume that there exists
a bridge (called `br-ext` in the following diagram) to which one of
your host's physical interfaces is connected.  The architecture would
look something like this:

                  +--------+
                  |        |
                  |  eth0  |
                  |        |
                  +----+---+
                       |    
                       |    
    +----------+  +----+---+
    |          |  |        |
    | docker0  |  | br-ext |
    |          |  |        |
    +----+-----+  +----+---+
         |             |    
         |             |    
    +----+-------------+---+
    |  eth0           eth1 |
    |                      |
    |  docker container    |
    |                      |
    +----------------------+

Each container will start with `eth0` managed by docker, and we will
add `eth1` after the container start using the [pipework][] script.

The `runpings.sh` script will:

- Build the `pinger` docker image.

- Launch a [coreos/etcd][] instance.

- Launch *N* instances of the `pinger` image.

Each `pinger` image will:

- Wait until an address is available on `eth1`.  The script will
  assign this address after launching the image using [pipework][].

- Register the address of `eth1` with the `etcd` instance.

And will then enter a loop:

- Query the `etcd` instance for all other registered pingers.

- Select one remote pinger at random and ping it 10 times.

It would be possible to accomplish almost the same thing using
single-interface containers and not relying on the [pipework][]
script, except that with current versions of docker it is not possible
assign specific ip addresses to containers (docker selects ones at
random from the range appropriate for the `docker0` bridge).  This is
sub-optimal if you are attaching your containers to a physical network
on which there are other hosts because it can lead to address
conflicts.

[coreos/etcd]: https://registry.hub.docker.com/u/coreos/etcd/

Set the following values in `runpingers.sh`:

- `BRIDGE` -- the name of the bridge over which to generate traffic.
- `BASEADDR` -- IP addresses will be assigned starting with this
  address and incrementing by one for each additional pinger.  The
  script is not smart about this; 255+1 is 256.
- `NETMASK` -- netmask to associate with the ip addresses
- `PIPEWORK` -- path to [pipework][] script.
- `NUMPINGERS` -- number of pingers to start.

[pipework]: https://github.com/jpetazzo/pipework

