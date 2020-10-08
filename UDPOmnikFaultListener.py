#!/usr/bin/python
import socket
import logging
from logging.config import fileConfig
import ConfigParser
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

# Load the logging settings
fileConfig(OmnikExport.expand_path('UDPOmnikFaultLogging.ini'))
logger = logging.getLogger()

serial = config.get('inverter', 'serial')

localIP = config.get('UDPListener', 'localIP')
localPort = int(config.get('UDPListener', 'localPort'))

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

logger.info("UDP Omnik Fault server up and listening on {0} on port {1}".format(localIP, localPort))

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(1024)

    #raw_msg = bytesAddressPair[0]
    msg = InverterMsg.InverterMsg(bytesAddressPair[0])
    sender = bytesAddressPair[1]

    logger.debug("{0}: Message from: {1}: ".format(datetime.datetime.now(), sender))

    if msg.status == 'NO INVERTER DATA':
        logger.error('Inverter Status Fault. Message:')
        logger.error('byte  ASC   HEX   CHR')
        logger.error('---------------------')
        n = 0
        for b in msg.raw_message:
            logger.error('{:>4} {:>4}   {}  {}'.format(n, b, hex(b), chr(b)))
            n = n + 1

    elif msg.aknowledge == 'DATA SEND IS OK':
        logger.debug('Aknowledgement message received: DATA SEND IS OK')

    elif msg.id == serial:
        logger.debug("Received data from ID: {0}".format(msg.id))

    else:
        logger.error('Unknown message received. Message:')
        logger.error('byte  ASC   HEX   CHR')
        logger.error('---------------------')
        n = 0
        for b in msg.raw_message:
            logger.error('{:>4} {:>4}   {}  {}'.format(n, b, hex(b), chr(b)))
            n = n + 1
