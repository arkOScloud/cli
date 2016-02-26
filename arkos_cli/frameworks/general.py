# -*- coding: utf-8 -*-
import click

from utils import CLIException


@click.command()
@click.pass_context
def version(ctx):
    """Show version and diagnostic details"""
    click.secho("arkOS-CLI version {}".format(ctx.obj["version"]), fg="green")
    if ctx.obj["conn_method"] == "remote":
        ctx.obj["client"].config.load()
        cfg = ctx.obj["client"].config._config
        click.echo(click.style(u" ↳ Connected to: ", fg="yellow") + ctx.obj["host"])
        click.echo(click.style(u" ↳ arkOS server version: ", fg="yellow") + cfg["enviro"].get("version", "unknown"))
        click.echo(click.style(u" ↳ arkOS arch/board: ", fg="yellow") + cfg["enviro"]["arch"] + " " + cfg["enviro"]["board"])
    if ctx.obj["conn_method"] == "local":
        from arkos import config
        click.echo(click.style(u" ↳ Connected to: ", fg="yellow") + "Local")
        click.echo(click.style(u" ↳ arkOS server version: ", fg="yellow") + config.get("enviro", "version", "unknown"))
        click.echo(click.style(u" ↳ arkOS arch/board: ", fg="yellow") + config.get("enviro", "arch") + " " + config.get("enviro", "board"))

GROUPS = [version]
