"""Sets up main command groups and authentication."""
import click
import os
import pyarkosclient
import sys

try:
    # Python 2
    import ConfigParser as configparser
except ImportError:
    # Python 3
    import configparser
from arkosctl.logs import LoggingControl

version = "0.3"
logger = LoggingControl()


def client():
    return click.get_current_context().obj["client"]


class CLIException(click.ClickException):
    """Reimplement click.ClickException() to print bold & in red."""

    def show(self, file=None):
        """Reimplement."""
        if self.message:
            logger.error("ctl:exc", self.format_message())


def get_arkosrc():
    """Get default configuration options from ~/.arkosrc."""
    default_map = {}
    if os.path.exists(os.path.join(os.path.expanduser("~"), ".arkosrc")):
        cfg = configparser.SafeConfigParser()
        cfg.read(os.path.join(os.path.expanduser("~"), ".arkosrc"))
        for n, v in cfg.items("arkosrc"):
            default_map[n] = v
    return default_map


def register_frameworks():
    from arkosctl.frameworks import (
        apikeys, applications, backups, certificates, databases, files,
        filesystems, networks, packages, roles, security, services, system,
        websites
    )

    modgroups = [
        apikeys.keys,
        applications.applications,
        backups.backups,
        certificates.certificates,
        databases.db,
        databases.db_users,
        files.files,
        files.links,
        filesystems.fs,
        networks.networks,
        packages.packages,
        roles.user,
        roles.group,
        roles.domain,
        security.security,
        services.services,
        system.system,
        websites.websites
    ]

    for x in modgroups:
        main.add_command(x)


@click.group(context_settings={"default_map": get_arkosrc()})
@click.option("--host", envvar="ARKOS_CLI_HOST", default="",
              help="Connect to remote arkOS server (host:port)")
@click.option("--user", envvar="ARKOS_CLI_USER", default="",
              help="Username for remote connection")
@click.option("--password", envvar="ARKOS_CLI_PASS", default="",
              help="Password for remote connection")
@click.option("--apikey", envvar="ARKOS_CLI_APIKEY", default="",
              help="API key for remote connection")
@click.option("-v/--verbose", envvar="ARKOS_CLI_VERBOSE", default=False,
              help="Verbose output")
@click.pass_context
def main(ctx, host, user, password, apikey, v):
    """Main command tree."""
    ctx.obj = {}
    logger.add_stream_logger(debug=v)
    if sys.argv[-1] == "--help":
        # Connection not required
        return
    if host and ((user and password) or apikey):
        try:
            ctx.obj["client"] = pyarkosclient.arkOS(
                host, user, password, api_key=apikey)
        except Exception as e:
            raise CLIException(str(e))
    else:
        raise CLIException(
            "No connection information specified for remote host.")


if __name__ == "__main__":
    register_frameworks()
    main()
else:
    register_frameworks()
