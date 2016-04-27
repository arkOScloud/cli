# -*- coding: utf-8 -*-
import click

from arkos_cli.utils import u, AliasedGroup, CLIException


@click.command(cls=AliasedGroup)
def system():
    """System commands"""
    pass

@system.command()
@click.pass_context
def shutdown(ctx):
    """Shutdown the system now"""
    if ctx.obj["conn_method"] == "remote":
        ctx.obj["client"].system.shutdown()
    elif ctx.obj["conn_method"] == "local":
        from arkos.system import sysconfig
        sysconfig.shutdown()
    click.echo("Shutdown initiated.")

@system.command()
@click.pass_context
def reboot(ctx):
    """Reboot the system now"""
    if ctx.obj["conn_method"] == "remote":
        ctx.obj["client"].system.reboot()
    elif ctx.obj["conn_method"] == "local":
        from arkos.system import sysconfig
        sysconfig.reboot()
    click.echo("Reboot initiated.")

@system.command()
@click.pass_context
def stats(ctx):
    """Show system statistics"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].system.get_stats()
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import stats
            data = stats.get_all()
    except Exception as e:
        raise CLIException(str(e))
    else:
        for x in list(data.keys()):
            click.echo("{0}: {1}".format(x, data[x]))

@click.command()
@click.pass_context
def version(ctx):
    """Show version and diagnostic details"""
    click.secho("arkOS-CLI version {0}".format(ctx.obj["version"]), fg="green")
    if ctx.obj["conn_method"] == "remote":
        ctx.obj["client"].config.load()
        cfg = ctx.obj["client"].config._config
        click.echo(click.style(u(" ↳ Connected to: "), fg="yellow") + ctx.obj["host"])
        click.echo(click.style(u(" ↳ arkOS server version: "), fg="yellow") + cfg["enviro"].get("version", "unknown"))
        click.echo(click.style(u(" ↳ arkOS arch/board: "), fg="yellow") + cfg["enviro"]["arch"] + " " + cfg["enviro"]["board"])
    elif ctx.obj["conn_method"] == "local":
        from arkos import config
        click.echo(click.style(u(" ↳ Connected to: "), fg="yellow") + "Local")
        click.echo(click.style(u(" ↳ arkOS server version: "), fg="yellow") + config.get("enviro", "version", "Unknown"))
        click.echo(click.style(u(" ↳ arkOS arch/board: "), fg="yellow") + config.get("enviro", "arch", "Unknown") + " " + config.get("enviro", "board", "Unknown"))


shutdown.aliases = ["halt"]
reboot.aliases = ["restart"]
stats.aliases = ["statistics", "uptime", "cpu", "ram", "temp", "temperature"]
GROUPS = [[version, "ver"], [system, "sys"]]
