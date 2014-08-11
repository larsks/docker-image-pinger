This was inspired by a conversation on IRC in `#docker`.

Set the following values in `runpingers.sh`:

- `BRIDGE` -- the name of the bridge over which to generate traffic.
- `BASEADDR` -- IP addresses will be assigned starting with this
  address and incrementing by one for each additional pinger.  The
  script is not smart about this; 255+1 is 256.
- `NETMASK` -- netmask to associate with the ip addresses
- `PIPEWORK` -- path to [pipework][] script.
- `NUMPINGERS` -- number of pingers to start.

