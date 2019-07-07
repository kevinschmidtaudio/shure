from socket import *
from console import two_digits
from config import *
import threading
from time import sleep


class Receiver:
    def __init__(self, ip, con):
        self.ip = ip
        self.port = 2202
        self.con = con
        self.batt = 255
        self.dbm = -128
        self.chan_name = "QLXD    "
        self.tx_on = False


    def print_values(self):
        """Print out values for testing purposes."""
        print("ip=" + self.ip + " \tname=" + self.chan_name + "\ttx_on=" + str(self.tx_on) + "  \tbatt=" + str(self.batt) + "\tdBm=" + str(self.dbm))

    def update_console(self):
        # Attempt to find the first matching channel.
        try:
            matched_ch = self.con.name_list.index(self.chan_name) + 1
        except:
            return -1

        color_message = "/ch/" + two_digits(matched_ch) + "/config/color"
        name_message = "/ch/" + two_digits(matched_ch) + "/config/name"

        # Light up channel strip when TX is on and change color according to battery level.
        if self.tx_on == True:
            if self.batt == 255:
                self.con.message(color_message, [7])
                print(self.chan_name + " (Channel " + str(matched_ch) + ") = On")
            elif 2 < self.batt <= 5:
                self.con.message(color_message, [7])
                print(self.chan_name + " (Channel " + str(matched_ch) + ") = On     Battery = " + str(self.batt * 20) + "%")
            elif self.batt <= 2:
                print(self.chan_name + " (Channel " + str(matched_ch) + ") = On     Battery = " + str(self.batt * 20) + "%")
                self.blink = threading.Thread(target=self.blinker, args=(color_message,))
                self.blink.start()

        # Turn channel strip color off when TX is off.
        elif self.tx_on == False:
            self.con.message(color_message, [0])
            print(self.chan_name + " (Channel " + str(matched_ch) + ") = Off")

        # Add battery info to channel name if battery information is available.
        if 1 < self.batt <= 5:
            value = bytes(self.chan_name + " (" + str(self.batt) + ")", 'utf-8')
            self.con.message(name_message, [value])

        # Change channel name to "Low Batt" if the battery 1 bar or below.
        elif self.batt <= 1:
            value = bytes("Low Batt (" + str(self.batt) + ")", 'utf-8')
            self.con.message(name_message, [value])

        # Remove battery info from channel name when no information.
        elif self.batt == 255:
            value = bytes(self.chan_name, 'utf-8')
            self.con.message(name_message, [value])

    def parser(self, data):
        """Parse the received data and store in the class variables when an appropriate update arrives."""
        pieces = data.split(" ")
        change = False
        if "SAMPLE" in pieces[1]:
            old = self.dbm
            self.dbm = int(pieces[5]) - 128
            # TODO
            #if old != self.dbm:
                #print("dBm has changed")
                #change = True
            if "XX" in pieces[4]:
                old = self.tx_on
                self.tx_on = False
                if old != self.tx_on:
                    change = True
            elif "AX" in pieces[4] or "XB" in pieces[4]:
                old = self.tx_on
                self.tx_on = True
                if old != self.tx_on:
                    change = True
        elif "REP" in pieces[1] and "BATT_BARS" in pieces[3]:
            old = self.batt
            self.batt = int(pieces[4])
            if old != self.batt:
                change = True
        elif "CHAN_NAME" in pieces[3]:
            old = self.chan_name
            self.chan_name = data[21:29]
            self.chan_name = self.chan_name.strip()
            if old != self.chan_name:
                change = True
        else:
            return -1
        #self.print_values()
        if change == True:
            self.update_console()

    def poller(self):
        """Connects to the actual QLXD receiver, sends commands, and received responses.
        Poller should be run inside of a thread, one for each receiver."""

        #try:
        # Connect to receiver
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((self.ip, self.port))

        # Send command strings to start metering and get all information
        sock.send(b"< SET 1 METER_RATE 00200 >")
        sock.send(b"< GET 1 ALL >")
        print(BLUE + "Listening to receiver at", self.ip + ENDC)

        # Wait for responses and call parser each time there is a response.
        while True:
            data = sock.recv(1024)
            self.parser(str(data))

        #except:
            #print(RED + "Connection to", self.ip, "has failed permanently!" + ENDC)

    def blinker(self, color_message):
        while True:
            if self.batt == 2:
                self.con.message(color_message, [3])
                sleep(0.75)
                self.con.message(color_message, [7])
                sleep(0.75)

            elif self.batt == 1:
                self.con.message(color_message, [1])
                sleep(0.5)
                self.con.message(color_message, [9])
                sleep(0.5)

            elif self.batt == 0:
                self.con.message(color_message, [1])
                sleep(0.25)
                self.con.message(color_message, [9])
                sleep(0.25)

            elif self.batt == 255:
                self.con.message(color_message, [0])
                return
            elif self.batt > 2:
                return