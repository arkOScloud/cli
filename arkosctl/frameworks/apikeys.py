# -*- coding: utf-8 -*-
"""Relates to commands for management of API keys."""
import click
import os

from arkosctl import client, logger, CLIException


try:
    # Python 2
    import ConfigParser as configparser
except ImportError:
    # Python 3
    import configparser


@click.group()
def keys():
    """API Keys commands."""
    pass


@keys.command(name='list')
def list_keys():
    """List all API keys."""
    try:
        keys = client().apikeys.get()
        if not keys:
            logger.info('ctl:keys:list', 'No keys found')
            return
        llen = len(sorted(keys, key=lambda x: len(x["user"]))[-1].name)
        for x in keys:
            click.echo(
                click.style(
                    '{name: <45}'.format(name=x["key"]),
                    fg="white", bold=True) +
                click.style(
                    '{name: <{fill}}'.format(name=x["user"], fill=llen + 3),
                    fg="green") + "   " +
                click.style(x["comment"], fg="yellow")
            )
    except Exception as e:
        raise CLIException(str(e))


@keys.command()
@click.option("--comment", default="arkOS-CLI",
              help="Comment for the API key to have")
@click.option("--save", is_flag=True,
              help="Save this API key to your .arkosrc and use automatically")
@click.argument("user")
def create(user, comment, save):
    """Create a new API key."""
    try:
        x = client().apikeys.add(user, comment)
        key = x["key"]
        smsg = "Added new API key for {} with comment {}".format(user, comment)
        logger.success('ctl:keys:create', smsg)
        logger.info('ctl:keys:create', key)
        click.echo(click.style("Your new API key is: ", fg="yellow") + key)
        cmsg = "Do you want to save this key to your .arkosrc?"
        if save or click.confirm(cmsg):
            cfg = configparser.SafeConfigParser()
            rcpath = os.path.join(os.path.expanduser("~"), ".arkosrc")
            if not os.path.exists(rcpath):
                with open(rcpath, "w") as f:
                    cfg.add_section("arkosrc")
            else:
                cfg.read(rcpath)
            cfg.set("arkosrc", "apikey", key)
            with open(rcpath, "w") as f:
                cfg.write(f)
            click.secho("API key saved to your .arkosrc config.", bold=True)
    except Exception as e:
        raise CLIException(str(e))


@keys.command()
@click.argument("key")
def revoke(key):
    """Revoke an API key."""
    try:
        client().apikeys.revoke(key)
        logger.info('ctl:keys:revoke', 'API key revoked')
    except Exception as e:
        raise CLIException(str(e))
