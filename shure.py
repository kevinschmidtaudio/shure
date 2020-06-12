from receiver import *
from console import *
import threading


RX_IP_LIST = ["192.168.10.51", "192.168.10.52", "192.168.10.53", "192.168.10.54"]
CONSOLE_IP = "192.168.10.13"


# Setup console connection and poll for all channel names
con = Console(CONSOLE_IP)


# Subscribe to updates from console
sub = threading.Thread(target=con.subscribe)
sub.start()


# Setup polling for each QLXD receiver in the RX_IP_LIST
for ip in RX_IP_LIST:
    rec = Receiver(ip, con)
    poll = threading.Thread(target=rec.poller)
    poll.start()
