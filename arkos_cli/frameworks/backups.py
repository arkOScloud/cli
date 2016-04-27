# -*- coding: utf-8 -*-
"""Relates to commands for management of backups."""
import click

from arkos_cli.utils import u, AliasedGroup, handle_job, CLIException


@click.command(cls=AliasedGroup)
def backups():
    """Backup commands."""
    pass


def _list_backups(bkps):
    if not bkps:
        click.echo("No backups found")
    for x in sorted(bkps, key=lambda x: x["time"]):
        imsg = click.style(" (" + x["type"].capitalize() + ")", fg="yellow")
        click.echo(click.style(x["pid"], fg="green") + imsg)
        click.secho(u(" ↳ ID: ") + x["id"], fg="white")
        click.secho(u(" ↳ Backed up on ") + x["time"].strftime("%c"),
                    fg="white")


@backups.command()
@click.pass_context
def list(ctx):
    """List all backups."""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].backups.get()
        elif ctx.obj["conn_method"] == "local":
            from arkos import backup
            data = backup.get()
    except Exception as e:
        raise CLIException(str(e))
    else:
        _list_backups(data)


@backups.command()
@click.pass_context
def types(ctx):
    """List types of apps/sites that can create backups."""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].backups.get_types()
        elif ctx.obj["conn_method"] == "local":
            from arkos import backup
            data = backup.get_types()
    except Exception as e:
        raise CLIException(str(e))
    else:
        for x in data:
            imsg = click.style("(" + x["type"].capitalize() + ")", fg="yellow")
            click.echo(click.style(x["id"], fg="green") + " " + imsg)


@backups.command()
@click.argument("appid")
@click.pass_context
def create(ctx, appid):
    """Create a backup."""
    try:
        click.secho("Creating backup of {}...".format(appid),
                    fg="green")
        if ctx.obj["conn_method"] == "remote":
            job, data = ctx.obj["client"].backups.create(id=appid)
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            from arkos import backup
            backup.create(appid)
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Backup saved!", fg="yellow")


@backups.command()
@click.argument("id")
@click.pass_context
def restore(ctx, id):
    """Restore a backup by ID."""
    if "/" not in id:
        raise CLIException("Requires full backup ID with app ID and timestamp")
    id, tsp = id.split("/")
    click.secho("Restoring backup...", fg="green")
    try:
        if ctx.obj["conn_method"] == "remote":
            job, data = ctx.obj["client"].backups.restore(id=id, time=tsp)
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            from arkos import backup
            b = [x for x in backup.get() if x["id"] == (id + "/" + tsp)][0]
            backup.restore(b)
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Backup restored!", fg="yellow")


@backups.command()
@click.argument("id")
@click.pass_context
def delete(ctx, id):
    """Delete a backup."""
    if "/" not in id:
        excmsg = "Requires full backup ID with app ID and timestamp"
        raise click.ClickException(excmsg)
    id, tsp = id.split("/")
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].backups.delete(id=id, time=tsp)
        elif ctx.obj["conn_method"] == "local":
            from arkos import backup
            backup.remove(id, tsp)
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.echo("Backup deleted")


list.aliases = ["backups"]
types.aliases = ["list-types", "list-apps", "list-sites", "apps", "sites"]
create.aliases = ["add", "backup"]
delete.aliases = ["remove"]
GROUPS = [[backups, "bak"]]
