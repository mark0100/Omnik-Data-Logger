import PluginLoader


class InfoOutput(PluginLoader.Plugin):
    """Outputs the version info data from the Omnik inverter to stdout"""

    def process_message(self, msg):
        """Output the information from the inverter to stdout.

        Args:
            msg (InverterMsg.InverterMsg): Message to process
        """

        serial = self.config.get('inverter', 'serial')

        if msg.status == 'INVERTER DATA':
            self.logger.info('Inverter Status Fault. Message:')
            print 'ASC, HEX, CHR'
            for b in msg.raw_message:
                print(b, hex(b), chr(b))

        elif msg.aknowledge == 'DATA SEND IS OK':
            self.logger.debug('Aknowledgement message received: DATA SEND IS OK')
                
        elif msg.id == serial:

            print "Inverter serial number: {}".format(msg.id)
            print "Firmware version (main): {}".format(msg.firmware_main)
            print "Firmware version (slave): {}".format(msg.firmware_slave)

        else:
            self.logger.error('Unknown message received - Aborting. Message:')
            msg.dump()

            #sys.exit(1)

