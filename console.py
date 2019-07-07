from oscpy.server import OSCThreadServer
from socket import *
from time import sleep
from config import *


def two_digits(ch):
    if ch < 10:
        ch = "0" + str(ch)
    else:
        ch = str(ch)
    return ch


class Console:
    def __init__(self, console_ip):
        self.console_ip = console_ip
        self.console_port = 10023
        self.name_list = []

        # Initialize name_list with 32 empty strings.
        for n in range(32):
            self.name_list.append("")

        # Setup socket to console connection and start listening
        hostname = gethostname()
        local_ip = gethostbyname(hostname)
        self.server = OSCThreadServer(advanced_matching=True)
        self.sock = self.server.listen(address=local_ip, port=0, default=True)
        self.server.bind(b"/ch/../config/name", self.callback, sock=self.sock, get_address=True)
        print(BLUE + "Listening to console at", self.console_ip + ENDC)

        # Query for all channel names
        for ch in range(1, 33):
            ch = two_digits(ch)
            message = "/ch/" + ch + "/config/name"
            self.message(message, "")

    def callback(self, address, values):
        # Extract channel number from address string
        address = str(address)
        channel = int(address[6:8])

        # Extract channel name string
        values = str(values)
        name = values[2: -1]
        batt_indicator = name.find(" (")
        if batt_indicator > -1:
            name = name[:batt_indicator]
            value = bytes(name, 'utf-8')
            name_message = "/ch/" + two_digits(channel) + "/config/name"
            self.message(name_message, value)

        # Add channel name into the name list at the appropriate index
        self.name_list[channel - 1] = name
        self.duplicate_names(channel)

    def subscribe(self):
        # Subscribe to console updates via OSC /xremote command.
        while True:
            self.server.send_message(b"/xremote", "", self.console_ip, self.console_port, sock=self.sock, safer=True)
            sleep(5)

    def message(self, message, value):
        # Send one OSC message to console.
        self.server.send_message(bytes(message, 'utf-8'), value, self.console_ip, self.console_port, sock=self.sock, safer=True)

    def duplicate_names(self, ch):
        dups = []
        a = self.name_list[ch - 1]

        # Search through all values in self.name_list and compare with ch.
        # Do not compare to itself, ignore blank channels.
        for y in range(32):
            b = self.name_list[y]
            if (ch - 1) != y:
                if a == b and a != "":
                    dups.append(ch)
                    dups.append(y + 1)

        # Report duplicate channels from temporary duplicate list, sort, and print warning message.
        dups = list(set(dups))
        dups.sort()
        if len(dups) > 1:
            print(YELLOW + 'Warning: Duplicate channel name!  Channels ' + str(dups)[1:-1] + ' = ' + self.name_list[ch - 1] + ENDC)