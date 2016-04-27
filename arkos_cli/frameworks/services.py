# -*- coding: utf-8 -*-
import click

from arkos_cli.utils import u, CLIException


@click.group()
def services():
    """Service commands"""
    pass


@services.command()
@click.argument("name")
@click.pass_context
def start(ctx, name):
    """Start a service"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].services.start(name)
            svc = ctx.obj["client"].services.get(id=name)
            state = svc["state"]
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import services
            svc = services.get(name)
            svc.start()
            state = svc.state
    except Exception as e:
        raise CLIException(str(e))
    else:
        if state == "running":
            click.secho("{} running".format(name), fg="green")
        else:
            click.secho("{} NOT running".format(name), fg="red")

@services.command()
@click.argument("name")
@click.pass_context
def stop(ctx, name):
    """Stop a service"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].services.stop(name)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import services
            svc = services.get(name)
            svc.stop()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("{} stopped".format(name), fg="red")

@services.command()
@click.argument("name")
@click.pass_context
def restart(ctx, name):
    """Restart a service"""
    try:
        if ctx.obj["conn_method"] == "remote":
            svc = ctx.obj["client"].services.restart(name)
            state = svc["state"]
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import services
            svc = services.get(name)
            svc.restart()
            state = svc.state
    except Exception as e:
        raise CLIException(str(e))
    else:
        if state == "running":
            click.secho("{} running".format(name), fg="green")
        else:
            click.secho("{} NOT running".format(name), fg="red")

@services.command()
@click.argument("name")
@click.pass_context
def enable(ctx, name):
    """Enable a service on boot"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].services.enable(name)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import services
            svc = services.get(name)
            svc.enable()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("{} enabled".format(name), fg="green")

@services.command()
@click.argument("name")
@click.pass_context
def disable(ctx, name):
    """Disable a service on boot"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].services.disable(name)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import services
            svc = services.get(name)
            svc.disable()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("{} disabled".format(name), fg="red")

@services.command()
@click.argument("name")
@click.pass_context
def status(ctx, name):
    """Get service status"""
    try:
        if ctx.obj["conn_method"] == "remote":
            svc = ctx.obj["client"].services.get(id=name)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import services
            svc = services.get(name).as_dict
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.echo(click.style(name, fg="green") + click.style(" ({0})".format(svc["state"].capitalize()),
            fg="yellow" if svc["state"] == "running" else "red"))
        click.secho(u(" ↳ Type: {0}").format(svc["type"].capitalize()), fg="white")
        click.secho(u(" ↳ Enabled on boot: {0}").format("Yes" if svc["enabled"] else "No"), fg="white")


GROUPS = [[services, "service", "svc"]]
