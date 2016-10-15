# -*- coding: utf-8 -*-
"""Relates to the management of filesystems."""
import click

from arkosctl import client, CLIException, logger
from arkosctl.utils import handle_job, str_fsize


@click.group()
def fs():
    """Filesystem commands."""
    pass


@fs.command(name='list')
def list_filesystems():
    """List filesystems"""
    try:
        data = client().filesystems.get()
        for x in data:
            click.echo(
                click.style(x["id"], fg="white", bold=True) +
                click.style(" (" + x["path"] + ")", fg="green")
            )
            click.echo(
                click.style(" * Type: ", fg="yellow") +
                x["fstype"].capitalize()
            )
            click.echo(
                click.style(" * Size: ", fg="yellow") +
                str_fsize(x["size"])
            )
            click.echo(
                click.style(" * Encrypted: ", fg="yellow") +
                ("Yes" if x["crypt"] else "No")
            )
            click.echo(
                click.style(" * Mounted: ", fg="yellow") +
                ("At " + x["mountpoint"] if x["mountpoint"] else "No")
            )
    except Exception as e:
        raise CLIException(str(e))


@fs.command()
@click.argument("name")
@click.option(
    "--size", required=True, type=int, prompt="Size of the new disk (in MB)",
    help="Size of the new disk (in MB)")
@click.option("--encrypt", is_flag=True, prompt="Encrypt this filesystem?",
              help="Encrypt this filesystem?")
@click.option("--password", help="Password (if encrypted filesystem)")
def create(name, size, encrypt, password):
    """Create a virtual disk."""
    try:
        if encrypt and not password:
            password = click.prompt(
                "Please choose a password for encryption",
                hide_input=True, confirmation_prompt=True)
        job, data = client().filesystems.create_virtual(
            name, size * 1048576, encrypt, password)
        handle_job(job)
    except Exception as e:
        raise CLIException(str(e))


@fs.command()
@click.argument("id")
@click.option("--password", help="Password (if encrypted filesystem)")
def mount(id, password):
    """Mount a filesystem"""
    try:
        fs = client().filesystems.get(id=id)
        if fs["crypt"] and not password:
            password = click.prompt(
                "Please enter your password to mount this filesystem",
                hide_input=True)
        client().filesystems.mount(id, password or "")
        logger.success('ctl:fs:mount', 'Mounted {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@fs.command()
@click.argument("id")
def umount(id):
    """Unmount a filesystem"""
    try:
        client().filesystems.umount(id)
        logger.success('ctl:fs:umount', 'Unmounted {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@fs.command()
@click.argument("id")
def enable(id):
    """Mount a filesystem on boot"""
    try:
        client().filesystems.enable(id)
        logger.success('ctl:fs:enable', 'Enabled {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@fs.command()
@click.argument("id")
def disable(id):
    """Disable mounting a filesystem on boot"""
    try:
        client().filesystems.disable(id)
        logger.success('ctl:fs:disable', 'Disabled {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@fs.command()
@click.argument("id")
def delete(id):
    """Delete a virtual disk"""
    try:
        client().filesystems.delete(id)
        logger.success('ctl:fs:delete', 'Deleted {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))
