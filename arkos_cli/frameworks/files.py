# -*- coding: utf-8 -*-
"""Relates to the management of files."""
import click

from arkos_cli.utils import u, AliasedGroup, CLIException


@click.command(cls=AliasedGroup)
def files():
    """File commands."""
    pass


@files.command()
@click.pass_context
def list_shares(ctx):
    """List all fileshare links."""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].files.get_shares()
        elif ctx.obj["conn_method"] == "local":
            from arkos import shared_files
            data = [x.as_dict for x in shared_files.get()]
    except Exception as e:
        raise CLIException(str(e))
    else:
        for x in data:
            smsg = click.style(x["path"], fg="green")
            click.echo(smsg + " ({0})".format(x["id"]))
            s = "Never" if not x["expires"] else x["expires_at"].strftime("%c")
            click.secho(u(" ↳ Expires: {0}").format(s), fg="white")


@files.command()
@click.argument("path")
@click.option("--expires", default=0, help="Unix timestamp for when the share "
              "link should expire, or 0 to last forever")
@click.pass_context
def add_share(ctx, path, expires):
    """Create a fileshare link."""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].files.share(path, expires)
        elif ctx.obj["conn_method"] == "local":
            from arkos import shared_files
            from arkos.utils import random_string
            share = shared_files.Share(random_string(), path, expires)
            share.add()
            data = share.serialized
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Share created!", fg="green")
        smsg = "Link is your external server address, plus: /shared/{0}"
        click.echo(smsg.format(data["id"]))


@files.command()
@click.argument("id")
@click.option("--expires", default=0, help="Unix timestamp for when the share "
              "link should expire, or 0 to last forever")
@click.pass_context
def update_share(ctx, id, expires):
    """Update a fileshare link's expiration."""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].files.update_share(id, expires)
        elif ctx.obj["conn_method"] == "local":
            from arkos import shared_files
            share = shared_files.get(id)
            share.update_expiry(expires)
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Share updated!", fg="green")


@files.command()
@click.argument("id")
@click.pass_context
def remove_share(ctx, id):
    """Disable a fileshare link."""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].files.remove_share(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos import shared_files
            share = shared_files.get(id)
            share.delete()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.echo("Share removed")


@files.command()
@click.argument("path")
@click.argument("out_path", type=click.File("wb"))
@click.pass_context
def download(ctx, path, out_path):
    """Download a file/folder from the server (remote connections only)."""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].files.download(path)
            with open(out_path, "w") as f:
                f.write(data.encode("utf-8"))
    except Exception as e:
        raise CLIException(str(e))


@files.command()
@click.argument("path")
@click.pass_context
def edit(ctx, path):
    """Open a file in your default editor."""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].files.get(path, content=True)
            out = click.edit(data["content"])
            if out:
                ctx.obj["client"].files.edit(path, out)
                click.secho("File saved as {}".format(path), bold=True)
            else:
                click.secho("File not saved.", bold=True)
        elif ctx.obj["conn_method"] == "local":
            with open(path, "r") as f:
                out = click.edit(f.read())
            if out:
                with open(path, "w") as f:
                    f.write(out)
                click.secho("File saved as {}".format(path), bold=True)
            else:
                click.secho("File not saved.", bold=True)
    except Exception as e:
        raise CLIException(str(e))


list_shares.aliases = ["list-shares", "shares"]
add_share.aliases = ["add-share", "new-share", "create-share",
                     "share", "share-url"]
update_share.aliases = ["update-share", "edit-share", "expire-share"]
remove_share.aliases = ["remove-share", "delete-share"]
GROUPS = [[files, "file", "shares", "share"]]
