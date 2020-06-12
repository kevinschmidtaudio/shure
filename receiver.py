from socket import *
from console import two_digits
import threading
from time import sleep


class Receiver:
    def __init__(self, ip, con):
        self.ip = ip
        self.port = 2202
        self.con = con
        self.batt_bars = 255
        self.dbm = -128
        self.chan_name = "QLXD    "
        self.tx_on = False
        self.tx_type = "UNKN"
        self.batt_type = "UNKN"
        self.run_time = 65536


    def print_values(self):
        """Print out values for testing purposes."""
        #print("ip=" + self.ip + " \tname=" + self.chan_name + "    \ttx_on=" + str(self.tx_on) + "    \tdBm=" + str(self.dbm))
        #print("batt_bars=" + str(self.batt_bars) + "    \tbatt_type=" + str(self.batt_type) + "    \trun_time=" + str(self.run_time) + "    \ttx_type=" + str(self.tx_type))

    def update_console(self):
        # Attempt to find the first matching channel.
        try:
            matched_ch = self.con.name_list.index(self.chan_name) + 1
        except:
            return -1

        color_message = "/ch/" + two_digits(matched_ch) + "/config/color"
        name_message = "/ch/" + two_digits(matched_ch) + "/config/name"
        icon_message = "/ch/" + two_digits(matched_ch) + "/config/icon"

        # Change channel icon to handheld or bodypack icons based on tx_type information.
        if self.tx_type == "QLXD1":
            self.con.message(icon_message, [53])
            print(self.chan_name + " (Channel " + str(matched_ch) + ") = On     Transmitter = QLXD1")
        elif self.tx_type == "QLXD2":
            self.con.message(icon_message, [51])
            print(self.chan_name + " (Channel " + str(matched_ch) + ") = On     Transmitter = QLXD2")
        else:
            self.con.message(icon_message, [1])

        # Light up channel strip when TX is on and change color according to battery level.
        if self.tx_on == True:
            if self.batt_bars == 255:
                self.con.message(color_message, [7])
                print(self.chan_name + " (Channel " + str(matched_ch) + ") = On")
            elif 2 < self.batt_bars <= 5:
                self.con.message(color_message, [7])
                print(self.chan_name + " (Channel " + str(matched_ch) + ") = On     Battery Bars = " + str(self.batt_bars) + "/5")
            elif self.batt_bars <= 2:
                print(self.chan_name + " (Channel " + str(matched_ch) + ") = On     Battery Bars = " + str(self.batt_bars) + "/5")
                self.blink = threading.Thread(target=self.blinker, args=(color_message,))
                self.blink.start()

        # Turn channel strip color off when TX is off.
        elif self.tx_on == False:
            self.con.message(color_message, [0])
            print(self.chan_name + " (Channel " + str(matched_ch) + ") = Off")

        # Add battery info to channel name if battery information is available.
        if self.batt_type == "LION" and self.run_time < 1000:
            # Add run time information if using Shure lithium batteries.
            value = bytes(self.chan_name + " " + self.hours_minutes(), 'utf-8')
            print(self.chan_name + " (Channel " + str(matched_ch) + ") = On     Run Time = " + self.hours_minutes())
            self.con.message(name_message, [value])

        else:
            if 0 <= self.batt_bars <= 5:
                value = bytes(self.chan_name + " (" + str(self.batt_bars) + ")", 'utf-8')
                self.con.message(name_message, [value])

            # Change channel name to "Lo Batt" if the battery 1 bar or below.
            #elif self.batt_bars <= 1:
                #value = bytes("Lo Batt (" + str(self.batt_bars) + ")", 'utf-8')
                #self.con.message(name_message, [value])

            # Remove battery info from channel name when no information.
            elif self.batt_bars == 255:
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
            old = self.batt_bars
            self.batt_bars = int(pieces[4])
            if old != self.batt_bars:
                change = True
        elif "REP" in pieces[1] and "BATT_TYPE" in pieces[3]:
            old = self.batt_type
            self.batt_type = str(pieces[4])
            if old != self.batt_type:
                change = True
        elif "REP" in pieces[1] and "BATT_RUN_TIME" in pieces[3]:
            old = self.run_time
            self.run_time = int(pieces[4])
            if old != self.run_time:
                change = True
        elif "REP" in pieces[1] and "TX_TYPE" in pieces[3]:
            old = self.tx_type
            self.tx_type = str(pieces[4])
            if old != self.tx_type:
                change = True
        elif "CHAN_NAME" in pieces[3]:
            old = self.chan_name
            self.chan_name = data[21:29]
            self.chan_name = self.chan_name.strip()
            if old != self.chan_name:
                change = True
        else:
            return -1
        self.print_values()
        if change == True:
            self.update_console()

    def poller(self):
        """Connects to the actual QLXD receiver, sends commands, and received responses.
        Poller should be run inside of a thread, one for each receiver."""

        try:
            # Connect to receiver
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((self.ip, self.port))

            # Send command strings to start metering and get all information
            sock.send(b"< SET 1 METER_RATE 00200 >")
            sock.send(b"< GET 1 ALL >")
            print("Listening to receiver at", self.ip)

            # Wait for responses and call parser each time there is a response.
            while True:
                data = sock.recv(1024)
                #print(str(data))
                self.parser(str(data))

        except:
            print("Connection to", self.ip, "has failed permanently!")

    def blinker(self, color_message):
        while True:
            if self.batt_bars == 2:
                self.con.message(color_message, [3])
                sleep(0.75)
                self.con.message(color_message, [7])
                sleep(0.75)

            elif self.batt_bars == 1:
                self.con.message(color_message, [1])
                sleep(0.5)
                self.con.message(color_message, [9])
                sleep(0.5)

            elif self.batt_bars == 0:
                self.con.message(color_message, [1])
                sleep(0.25)
                self.con.message(color_message, [9])
                sleep(0.25)

            elif self.batt_bars == 255:
                self.con.message(color_message, [0])
                return
            elif self.batt_bars > 2:
                return

    def hours_minutes(self):
        # Convert run time into h:mm string.
        hours = int(self.run_time / 60)
        minutes = self.run_time % 60
        minutes = two_digits(minutes)
        hour_min = str(hours) + ":" + str(minutes)
        #print(hour_min)
        return hour_min
