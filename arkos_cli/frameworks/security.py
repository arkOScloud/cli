# -*- coding: utf-8 -*-
import click

from arkos_cli.utils import u, CLIException


@click.group()
def security():
    """Security commands"""
    pass

@security.command()
@click.pass_context
def list(ctx):
    """List security policies"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].security.get_policies()
        elif ctx.obj["conn_method"] == "local":
            from arkos import tracked_services
            data = [x.serialized for x in tracked_services.get()]
    except Exception as e:
        raise CLIException(str(e))
    else:
        for x in data:
            pol, fg = ("Allow All", "green") if x["policy"] == 2 else (("Local Only", "yellow") if x["policy"] == 1 else ("Restricted", "red"))
            click.echo(click.style(x["name"], fg="green") + click.style(" (" + x["id"] +")", fg="yellow"))
            click.secho(u(" ↳ Type: {0}").format(x["type"]), fg="white")
            click.secho(u(" ↳ Ports: {0}").format(", ".join(["{0} {1}".format(y[1], y[0].upper()) for y in x["ports"]])), fg="white")
            click.echo(click.style(u(" ↳ Policy: "), fg="white") + click.style(pol, fg=fg))

@security.command()
@click.argument("id")
@click.pass_context
def allow(ctx, id):
    """Allow all access to service"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].security.update_policy(id, "allow")
        elif ctx.obj["conn_method"] == "local":
            from arkos import tracked_services
            svc = tracked_services.get(id)
            svc.policy = 2
            svc.save()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.echo("Access to service allowed")

@security.command()
@click.argument("id")
@click.pass_context
def local(ctx, id):
    """Allow local network access only to service"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].security.update_policy(id, "local")
        elif ctx.obj["conn_method"] == "local":
            from arkos import tracked_services
            svc = tracked_services.get(id)
            svc.policy = 1
            svc.save()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.echo("Access to service restricted to local")

@security.command()
@click.argument("id")
@click.pass_context
def block(ctx, id):
    """Block all network access to service"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].security.update_policy(id, "block")
        elif ctx.obj["conn_method"] == "local":
            from arkos import tracked_services
            svc = tracked_services.get(id)
            svc.policy = 0
            svc.save()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.echo("Access to service blocked")


GROUPS = [[security, "policies", "policy"]]
