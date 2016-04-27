# -*- coding: utf-8 -*-
"""Relates to the management of filesystems."""
import click

from arkos_cli.utils import u, AliasedGroup, handle_job, CLIException, str_fsize


@click.command(cls=AliasedGroup)
def filesystems():
    """Filesystem commands."""
    pass


@filesystems.command()
@click.pass_context
def list(ctx):
    """List filesystems"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].filesystems.get()
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import filesystems
            data = [x.serialized for x in filesystems.get()]
    except Exception as e:
        raise CLIException(str(e))
    else:
        for x in data:
            click.echo(click.style(x["id"], fg="green") + click.style(" (" + x["path"] +")", fg="yellow"))
            click.secho(u(" ↳ Type: {0} {1}").format(x["type"].capitalize(), x["fstype"]), fg="white")
            click.secho(u(" ↳ Size: {0}").format(str_fsize(x["size"])),
                        fg="white")
            click.secho(u(" ↳ Encrypted: {0}").format("Yes" if x["crypt"] else "No"), fg="white")
            click.secho(u(" ↳ Mounted: {0}").format("At " + x["mountpoint"] if x["mountpoint"] else "No"), fg="white")


@filesystems.command()
@click.argument("name")
@click.option("--size", required=True, type=int, prompt="Size of the new disk (in MB)",
              help="Size of the new disk (in MB)")
@click.option("--encrypt", is_flag=True, prompt="Encrypt this filesystem?",
              help="Encrypt this filesystem?")
@click.option("--password", help="Password (if encrypted filesystem)")
@click.pass_context
def create(ctx, name, size, encrypt, password):
    """Create a virtual disk."""
    try:
        if encrypt and not password:
            password = click.prompt("Please choose a password to encrypt this encrypted filesystem with",
                hide_input=True, confirmation_prompt=True)
        if ctx.obj["conn_method"] == "remote":
            job, data = ctx.obj["client"].filesystems.create_virtual(name, size * 1048576,
                encrypt, password)
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import filesystems
            click.echo("Creating and encrypting virtual disk...")
            fs = filesystems.VirtualDisk(id=name, size=size * 1048576)
            fs.create()
            if encrypt:
                fs.encrypt(password)
            click.secho("Virtual disk created", fg="green")
    except Exception as e:
        raise CLIException(str(e))

@filesystems.command()
@click.argument("id")
@click.option("--password", help="Password (if encrypted filesystem)")
@click.pass_context
def mount(ctx, id, password):
    """Mount a filesystem"""
    try:
        if ctx.obj["conn_method"] == "remote":
            fs = ctx.obj["client"].filesystems.get(id=id)
            if fs["crypt"] and not password:
                password = click.prompt("Please enter your password to mount this encrypted filesystem",
                    hide_input=True)
            ctx.obj["client"].filesystems.mount(id, password or "")
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import filesystems
            fs = filesystems.get(id)
            if fs.crypt and not password:
                password = click.prompt("Please enter your password to mount this encrypted filesystem",
                    hide_input=True)
            fs.mount(password)
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Filesystem mounted", fg="green")

@filesystems.command()
@click.argument("id")
@click.pass_context
def umount(ctx, id):
    """Unmount a filesystem"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].filesystems.umount(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import filesystems
            fs = filesystems.get(id)
            fs.umount()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Filesystem unmounted", fg="red")

@filesystems.command()
@click.argument("id")
@click.pass_context
def enable(ctx, id):
    """Mount a filesystem on boot"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].filesystems.enable(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import filesystems
            fs = filesystems.get(id)
            fs.enable()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Filesystem enabled", fg="green")

@filesystems.command()
@click.argument("id")
@click.pass_context
def disable(ctx, id):
    """Disable mounting a filesystem on boot"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].filesystems.disable(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import filesystems
            fs = filesystems.get(id)
            fs.disable()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Filesystem disabled", fg="red")

@filesystems.command()
@click.argument("id")
@click.pass_context
def delete(ctx, id):
    """Delete a virtual disk"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].filesystems.delete(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import filesystems
            fs = filesystems.get(id)
            fs.remove()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Filesystem deleted", fg="red")


list.aliases = ["filesystems", "disks"]
create.aliases = ["add", "new"]
umount.aliases = ["unmount"]
delete.aliases = ["remove", "erase"]
GROUPS = [[filesystems, "filesystem", "fs", "disk", "disks"]]
