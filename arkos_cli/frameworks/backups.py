# -*- coding: utf-8 -*-
import click
import time


@click.group()
def backups():
    """Backups commands"""
    pass


def _list_backups(bkps):
    if not bkps:
        click.echo("No backups found")
    for x in sorted(bkps, key=lambda x: x["time"]):
        click.echo(click.style(x["pid"], fg="green") + click.style(" (" + x["type"].capitalize() +")", fg="yellow"))
        click.secho(u" ↳ ID: " + x["id"], fg="white")
        click.secho(u" ↳ Backed up on " + x["time"].strftime("%c"), fg="white")


@backups.command()
@click.pass_context
def list(ctx):
    """List all backups"""
    if ctx.obj["conn_method"] == "remote":
        _list_backups(ctx.obj["client"].backups.get())

@backups.command()
@click.pass_context
def types(ctx):
    """List types of apps/sites that can create backups"""
    if ctx.obj["conn_method"] == "remote":
        for x in ctx.obj["client"].backups.get_types():
            click.echo(click.style(x["id"], fg="green") + click.style(" (" + x["type"].capitalize() +")", fg="yellow"))

@backups.command()
@click.argument("appid")
@click.pass_context
def create(ctx, appid):
    """Create a backup"""
    if ctx.obj["conn_method"] == "remote":
        job, data = ctx.obj["client"].backups.create(id=appid)
        click.secho("Creating backup of {}...".format(data["pid"]), fg="green")
        while job.status == "running":
            time.sleep(2)
            job.check()
        click.secho("Backup saved!", fg="yellow")

@backups.command()
@click.argument("id")
@click.pass_context
def restore(ctx, id):
    """Restore a backup by ID"""
    if not "/" in id:
        raise click.ClickException("Requires full backup ID with app ID and timestamp")
    id, tsp = id.split("/")
    if ctx.obj["conn_method"] == "remote":
        job, data = ctx.obj["client"].backups.restore(id=id, time=tsp)
        click.secho("Restoring backup...", fg="green")
        while job.status == "running":
            time.sleep(2)
            job.check()
        click.secho("Backup restored!", fg="yellow")

@backups.command()
@click.argument("id")
@click.pass_context
def delete(ctx, id):
    """Delete a backup"""
    if not "/" in id:
        raise click.ClickException("Requires full backup ID with app ID and timestamp")
    id, tsp = id.split("/")
    if ctx.obj["conn_method"] == "remote":
        ctx.obj["client"].backups.delete(id=id, time=tsp)
        click.echo("Backup deleted")


GROUPS = [backups]
