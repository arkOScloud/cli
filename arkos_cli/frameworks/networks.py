# -*- coding: utf-8 -*-
import click

from arkos_cli.utils import u, AliasedGroup, abort_if_false, CLIException, str_fsize


@click.command(cls=AliasedGroup)
def networks():
    """Network commands"""
    pass

@networks.command()
@click.pass_context
def list(ctx):
    """List system networks"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].networks.get()
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import networks
            data = [x.serialized for x in networks.get_connections()]
    except Exception as e:
        raise CLIException(str(e))
    else:
        for x in data:
            click.echo(click.style(x["id"], fg="green") + click.style(" (" + x["config"]["connection"].capitalize() +")", fg="yellow"))
            click.secho(u(" ↳ Addressing: {0}").format("DHCP" if x["config"]["ip"] == "dhcp" else x["config"]["ip"]), fg="white")
            click.secho(u(" ↳ Interface: {0}").format(x["config"]["interface"]), fg="white")
            click.secho(u(" ↳ Enabled: {0}").format("Yes" if x["enabled"] else "No"), fg="white")
            click.secho(u(" ↳ Connected: {0}").format("Yes" if x["connected"] else "No"), fg="white")

@networks.command()
@click.pass_context
def interfaces(ctx):
    """List system network interfaces"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].networks.get_interfaces()
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import networks
            data = [x.serialized for x in networks.get_interfaces()]
    except Exception as e:
        raise CLIException(str(e))
    else:
        for x in data:
            click.echo(click.style(x["id"], fg="green") + click.style(" (" + x["type"].capitalize() +")", fg="yellow"))
            click.secho(u(" ↳ Rx/Tx: {0} / {1}").format(str_fsize(x["rx"]), str_fsize(x["tx"])), fg="white")
            click.secho(u(" ↳ Connected: {0}").format("Yes" if x["up"] else "No"), fg="white")
            if x["ip"]:
                click.secho(u(" ↳ Address(es): {0}").format(", ".join([y["addr"]+"/"+y["netmask"] for y in x["ip"]])),
                    fg="white")

@networks.command()
@click.argument("id")
@click.pass_context
def connect(ctx, id):
    """Connect to a network"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].networks.connect(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import networks
            n = networks.get(id)
            n.connect()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Operation completed successfully", fg="green")

@networks.command()
@click.argument("id")
@click.pass_context
def disconnect(ctx, id):
    """Disconnect from a network"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].networks.disconnect(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import networks
            n = networks.get(id)
            n.disconnect()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Operation completed successfully", fg="green")

@networks.command()
@click.argument("id")
@click.pass_context
def enable(ctx, id):
    """Enable connection to a network on boot"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].networks.enable(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import networks
            n = networks.get(id)
            n.enable()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Operation completed successfully", fg="green")

@networks.command()
@click.argument("id")
@click.pass_context
def disable(ctx, id):
    """Disable connection to a network on boot"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].networks.disable(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import networks
            n = networks.get(id)
            n.disable()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Operation completed successfully", fg="green")

@networks.command()
@click.argument("id")
@click.pass_context
def delete(ctx, id):
    """Delete a network connection"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].networks.delete(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import networks
            n = networks.get(id)
            n.remove()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Operation completed successfully", fg="green")


list.aliases = ["list-networks", "list_networks"]
interfaces.aliases = ["list-interfaces", "list_interfaces"]
connect.aliases = ["up"]
disconnect.aliases = ["down"]
delete.aliases = ["remove"]
GROUPS = [[networks, "network", "net"]]
