This project monitors Shure QLX-D wireless mics receivers and outputs status feedback to an X32 or M32 mixing console.

The scribble strip will light up white when the receiver has a signal from a transmitter.  If the transmitter is turned off, the channel will go black.

When transmitter battery information is available, the number of battery bars will be appended to the channel name inside parenthesis.  Example: "Greg (4)"  If the battery falls too low, the channel strip will flash yellow/white for 2 bars, and red for 1 or 0 bars.  The channel strip name will be removed and replaced with "Low Batt" if the battery level is 1 or 0.



GETTING STARTED:

Ensure that the oscpy package is installed.  Console, receivers, and computer running Python script must be able to communicate over an IP network.

Use Wireless Workbench to edit the names of the receivers to be unique, and obtain IP addresses of each QLXD receiver.

Add console's IP address and a list of QLX-D receivers' IP addresses in the shure.py file.

  Example:
  
    RX_IP_LIST = ["192.168.10.125", "192.168.10.126", "192.168.10.127", "192.168.10.128"]
    
    CONSOLE_IP = "192.168.10.12"

Associate a specific Shure receiver with a specific channel on the mixing console by renaming the console channel as the same name as the Shure receiver.  The text is case sensitive and only supports a max of 8 characters.  Do not use parenthesis or a colon in the channel name.
