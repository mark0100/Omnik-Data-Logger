import socket
import sys
import logging
import logging.config
import ConfigParser
import os
from PluginLoader import Plugin
import InverterMsg  # Import the Msg handler
import datetime
from OmnikExport import OmnikExport

config = None
logger = None

# Load the setting
config_files = [OmnikExport.expand_path('config-default.cfg'),
                OmnikExport.expand_path('config.cfg')]

config = ConfigParser.RawConfigParser()
config.read(config_files)

serial = config.get('inverter', 'serial')

localIP = config.get('UDPListener', 'localIP')
localPort = int(config.get('UDPListener', 'localPort'))

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("{0}: UDP server up and listening on {1} on port {2}".format(datetime.datetime.now(), localIP, localPort))

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(1024)

    raw_msg = bytesAddressPair[0]
    msg = InverterMsg.InverterMsg(bytesAddressPair[0])
    sender = bytesAddressPair[1]

    print "{0}: Message from: {1}: ".format(datetime.datetime.now(), sender)

    if msg.status == 'INVERTER DATA':
        print('Inverter Status Fault. Message:')
        msg.dump()

    elif msg.aknowledge == 'DATA SEND IS OK':
        print('Aknowledgement message received: DATA SEND IS OK')
                
    elif msg.id == serial:

        print "ID: {0}".format(msg.id)

        print "E Today: {0:>5}   Total: {1:<5}".format(msg.e_today, msg.e_total)
        print "H Total: {0:>5}   Temp:  {1:<5}"\
            .format(msg.h_total, msg.temperature)

        print "PV1   V: {0:>5}   I: {1:>4}".format(msg.v_pv(1), msg.i_pv(1))
        print "PV2   V: {0:>5}   I: {1:>4}".format(msg.v_pv(2), msg.i_pv(2))
        print "PV3   V: {0:>5}   I: {1:>4}".format(msg.v_pv(3), msg.i_pv(3))

        print "L1    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}"\
            .format(msg.p_ac(1), msg.v_ac(1), msg.i_ac(1), msg.f_ac(1))
        print "L2    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}"\
            .format(msg.p_ac(2), msg.v_ac(2), msg.i_ac(2), msg.f_ac(2))
        print "L3    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}"\
            .format(msg.p_ac(3), msg.v_ac(3), msg.i_ac(3), msg.f_ac(3))

    else:
        print('Unknown message received. Message:')
        msg.dump()

    
