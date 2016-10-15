# -*- coding: utf-8 -*-
import click

from arkosctl import client, version, CLIException, logger


@click.group(name='sys')
def system():
    """System commands"""
    pass


@system.command()
def shutdown():
    """Shutdown the system now"""
    client().system.shutdown()
    logger.success('ctl:system:shutdown', 'Shutdown initiated')


@system.command()
def reboot():
    """Reboot the system now"""
    client().system.reboot()
    logger.success('ctl:system:reboot', 'Reboot initiated')


@system.command()
def stats():
    """Show system statistics"""
    try:
        data = client().system.get_stats()
        for x in list(data.keys()):
            click.echo("{0}: {1}".format(x, data[x]))
    except Exception as e:
        raise CLIException(str(e))


@system.command(name='version')
def show_version():
    """Show version and diagnostic details"""
    click.secho("arkOSctl version {0}".format(version), fg="green")
    client().config.load()
    cfg = client().config._config
    click.echo(
        click.style(" * arkOS server version: ", fg="yellow") +
        cfg["enviro"].get("version", "unknown")
    )
    click.echo(
        click.style(" * Arch / Board: ", fg="yellow") +
        cfg["enviro"].get("arch", "Unknown") + " / " +
        cfg["enviro"].get("board", "Unknown")
    )
