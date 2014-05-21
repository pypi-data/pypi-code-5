from circus.commands.base import Command


class GetDirectory(Command):
    """\
        Get node directory
        ==================

        Retrieve cluster node directory from arbiter.

        ZMQ Message
        -----------

        ::

            {
                "command": "getdirectory"
            }

        The response return the status "ok".


        Command line
        ------------

        ::

            $ circusctl getdirectory

    """
    name = "directory"

    def message(self, *args, **opts):
        return self.make_message()

    def execute(self, arbiter, opts):
        return {'directory': arbiter.nodes_directory}

    def console_msg(self, msg):
        if "directory" in msg:
            return "\n".join(["%s: %s" % (fqdn, endpoints)
                              for fqdn, endpoints in msg['directory'].items()])
        return self.console_error(msg)
