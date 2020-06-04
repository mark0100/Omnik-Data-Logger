import PluginLoader
import datetime
import urllib
import urllib2


class InverterFaultsOutput(PluginLoader.Plugin):
    """Log inverter faults to separate logfile"""

    def process_message(self, msg):
        """Log inverter faults to separate logfile

        Args:
            msg (InverterMsg.InverterMsg): Message to process

        """
        now = datetime.datetime.now()
        if msg.status == 'NO INVERTER DATA':
            self.logger.info('Inverter Status Fault. Message:')
            msg.dump()


