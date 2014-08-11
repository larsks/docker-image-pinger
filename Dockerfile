FROM fedora

RUN yum -y install python-requests

RUN mkdir /opt/pinger
ADD etcdclient.py /opt/pinger/etcdclient.py
ADD pinger.py /opt/pinger/pinger.py
WORKDIR /opt/pinger

CMD python pinger.py --verbose --endpoint http://etcd:4001/v2


