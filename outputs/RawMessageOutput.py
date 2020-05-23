import PluginLoader


class RawMessageOutput(PluginLoader.Plugin):
    """Outputs the version info data from the Omnik inverter to stdout"""

    def process_message(self, msg):
        """Output the information from the inverter to stdout.

        Args:
            msg (InverterMsg.InverterMsg): Message to process
        """

        msg.dump()

