# -*- coding: utf-8 -*-
import click

from arkosctl import client, CLIException, logger
from arkosctl.utils import str_fsize


@click.group(name='net')
def networks():
    """Network commands"""
    pass


@networks.command(name='list')
def list_networks():
    """List system networks"""
    try:
        data = client().networks.get()
        for x in data:
            click.echo(
                click.style(x["id"], fg="white", bold=True) +
                click.style(
                    " (" + x["config"]["connection"].capitalize() + ")",
                    fg="green"
                )
            )
            click.echo(
                click.style(" * Addressing: ", fg="yellow") +
                ("DHCP" if x["config"]["ip"] == "dhcp" else x["config"]["ip"])
            )
            click.echo(
                click.style(" * Interface: ", fg="yellow") +
                x["config"]["interface"]
            )
            click.echo(
                click.style(" * Enabled: ", fg="yellow") +
                ("Yes" if x["enabled"] else "No")
            )
            click.echo(
                click.style(" * Connected: ", fg="yellow") +
                ("Yes" if x["connected"] else "No")
            )
    except Exception as e:
        raise CLIException(str(e))


@networks.command(name='ifaces')
def list_interfaces():
    """List system network interfaces"""
    try:
        data = client().networks.get_interfaces()
        for x in data:
            click.echo(
                click.style(x["id"], fg="white", bold=True) +
                click.style(" (" + x["itype"].capitalize() + ")", fg="green")
            )
            click.echo(
                click.style(" * Rx/Tx: ", fg="yellow") +
                "{0} / {1}".format(str_fsize(x["rx"]), str_fsize(x["tx"]))
            )
            click.echo(
                click.style(" * Connected: ", fg="yellow") +
                ("Yes" if x["up"] else "No")
            )
            if x["ip"]:
                click.echo(
                    click.style(" * Address(es): ", fg="yellow") +
                    ", ".join([y["addr"]+"/"+y["netmask"] for y in x["ip"]])
                )
    except Exception as e:
        raise CLIException(str(e))


@networks.command()
@click.argument("id")
def connect(id):
    """Connect to a network"""
    try:
        client().networks.connect(id)
        logger.success('ctl:net:connect', 'Connected {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@networks.command()
@click.argument("id")
def disconnect(id):
    """Disconnect from a network"""
    try:
        client().networks.disconnect(id)
        logger.success('ctl:net:disconnect', 'Disconnected {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@networks.command()
@click.argument("id")
def enable(id):
    """Enable connection to a network on boot"""
    try:
        client().networks.enable(id)
        logger.success('ctl:net:enable', 'Enabled {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@networks.command()
@click.argument("id")
def disable(id):
    """Disable connection to a network on boot"""
    try:
        client().networks.disable(id)
        logger.success('ctl:net:disable', 'Disabled {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@networks.command()
@click.argument("id")
def delete(id):
    """Delete a network connection"""
    try:
        client().networks.delete(id)
        logger.success('ctl:net:delete', 'Deleted {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))
