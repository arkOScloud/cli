# -*- coding: utf-8 -*-
"""Relates to commands for management of backups."""
import click

from arkosctl import client, CLIException, logger
from arkosctl.utils import handle_job


@click.group(name='backup')
def backups():
    """Backup commands."""
    pass


def _list_backups(bkps):
    if not bkps:
        logger.info('ctl:bak:list', 'No backups found')
    for x in sorted(bkps, key=lambda x: x["time"]):
        imsg = click.style(" (" + x["type"].capitalize() + ")", fg="yellow")
        click.echo(click.style(x["pid"], fg="green", bold=True) + imsg)
        click.echo(
            click.style(" * Backed up on: ", fg="yellow") + x["time"]
        )


@backups.command()
def list():
    """List all backups."""
    try:
        data = client().backups.get()
        _list_backups(data)
    except Exception as e:
        raise CLIException(str(e))


@backups.command(name='types')
def backup_types():
    """List types of apps/sites that can create backups."""
    try:
        data = client().backups.get_types()
        for x in data:
            imsg = click.style("(" + x["type"].capitalize() + ")", fg="yellow")
            click.echo(
                click.style(x["id"], fg="green", bold=True) + " " + imsg
            )
    except Exception as e:
        raise CLIException(str(e))


@backups.command()
@click.argument("appid")
def create(appid):
    """Create a backup."""
    try:
        job, data = client().backups.create(id=appid)
        handle_job(job)
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Backup saved!", fg="yellow")


@backups.command()
@click.argument("id")
def restore(id):
    """Restore a backup by ID."""
    if "/" not in id:
        raise CLIException("Requires full backup ID with app ID and timestamp")
    id, tsp = id.split("/")
    try:
        job, data = client().backups.restore(id=id, time=tsp)
        handle_job(job)
    except Exception as e:
        raise CLIException(str(e))


@backups.command()
@click.argument("id")
def delete(id):
    """Delete a backup."""
    if "/" not in id:
        excmsg = "Requires full backup ID with app ID and timestamp"
        raise CLIException(excmsg)
    id, tsp = id.split("/")
    try:
        client().backups.delete(id=id, time=tsp)
    except Exception as e:
        raise CLIException(str(e))
