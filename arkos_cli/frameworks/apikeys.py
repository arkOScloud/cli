# -*- coding: utf-8 -*-
"""Relates to commands for management of API keys."""
import click
import os

try:
    # Python 2
    import ConfigParser as configparser
except ImportError:
    # Python 3
    import configparser

from arkos_cli.utils import AliasedGroup, CLIException


@click.command(cls=AliasedGroup)
def apikeys():
    """API Keys commands."""
    pass


@apikeys.command()
@click.pass_context
def list(ctx):
    """List all API keys."""
    try:
        if ctx.obj["conn_method"] == "remote":
            keys = ctx.obj["client"].apikeys.get()
        elif ctx.obj["conn_method"] == "local":
            from arkos import secrets
            keys = secrets.get_all("api-keys")
    except Exception as e:
        raise CLIException(str(e))
    else:
        if not keys:
            click.secho("No keys found", bold=True)
        for x in keys:
            smsg = click.style(" [{}] ({})".format(x["user"], x["comment"]))
            click.echo(x["key"] + smsg, fg="yellow")


@apikeys.command()
@click.option("--comment", default="arkOS-CLI",
              help="Comment for the API key to have")
@click.option("--save", is_flag=True,
              help="Save this API key to your .arkosrc and use automatically")
@click.argument("user")
@click.pass_context
def create(ctx, user, comment, save):
    """Create a new API key."""
    try:
        if ctx.obj["conn_method"] == "remote":
            x = ctx.obj["client"].apikeys.add(user, comment)
            key = x["key"]
        elif ctx.obj["conn_method"] == "local":
            from arkos import secrets
            from kraken.utilities import genAPIKey
            key = genAPIKey()
            kdata = {"key": key, "user": user, "comment": comment}
            secrets.append("api-keys", kdata)
            secrets.save()
    except Exception as e:
        raise CLIException(str(e))
    else:
        smsg = "Added new API key for {} with comment {}".format(user, comment)
        click.secho(smsg, fg="green")
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


@apikeys.command()
@click.argument("key")
@click.pass_context
def revoke(ctx, key):
    """Revoke an API key."""
    try:
        if ctx.obj["conn_method"] == "remote":
            x = ctx.obj["client"].apikeys.revoke(key)
        elif ctx.obj["conn_method"] == "local":
            from arkos import secrets
            data = secrets.get_all("api-keys")
            for x in data:
                if x["key"] == key:
                    data.remove(x)
                    secrets.save()
                    break
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("API key revoked")


create.aliases = ["add", "new", "generate"]
revoke.aliases = ["remove", "delete"]
GROUPS = [[apikeys, "api"]]
