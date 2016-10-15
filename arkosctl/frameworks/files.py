# -*- coding: utf-8 -*-
"""Relates to the management of files."""
import click

from arkosctl import client, CLIException, logger


@click.group(name='link')
def links():
    """Shared file commands."""
    pass


@click.group(name='file')
def files():
    """File commands."""
    pass


@links.command(name='list')
def list_shares():
    """List all fileshare links."""
    try:
        data = client().files.get_shares()
        for x in data:
            smsg = click.style(x["path"], fg="white", bold=True)
            click.echo(smsg + " ({0})".format(x["id"]))
            s = "Never" if not x["expires"] else x["expires_at"].strftime("%c")
            click.echo(click.style(" * Expires: ", fg="yellow") + s)
    except Exception as e:
        raise CLIException(str(e))


@links.command(name='create')
@click.argument("path")
@click.option("--expires", default=0, help="Unix timestamp for when the share "
              "link should expire, or 0 to last forever")
def add_share(path, expires):
    """Create a fileshare link."""
    try:
        data = client().files.share(path, expires)
        logger.success('ctl:links:create', 'Created link')
        smsg = "Link is your external server address, plus: /shared/{0}"
        logger.info('ctl:links:create', smsg.format(data["id"]))
    except Exception as e:
        raise CLIException(str(e))


@links.command(name='update')
@click.argument("id")
@click.option("--expires", default=0, help="Unix timestamp for when the share "
              "link should expire, or 0 to last forever")
def update_share(id, expires):
    """Update a fileshare link's expiration."""
    try:
        client().files.update_share(id, expires)
        logger.success('ctl:links:update', 'Updated share {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@links.command(name='delete')
@click.argument("id")
def remove_share(id):
    """Disable a fileshare link."""
    try:
        client().files.remove_share(id)
        logger.success('ctl:links:delete', 'Deleted share {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@files.command()
@click.argument("path")
@click.argument("out_path", type=click.File("wb"))
def download(path, out_path):
    """Download a file/folder from the server (remote connections only)."""
    try:
        data = client().files.download(path)
        with open(out_path, "w") as f:
            f.write(data.encode("utf-8"))
    except Exception as e:
        raise CLIException(str(e))


@files.command()
@click.argument("path")
def edit(path):
    """Open a file in your default editor."""
    try:
        data = client().files.get(path, content=True)
        out = click.edit(data["content"])
        if out:
            client().files.edit(path, out)
            logger.info('ctl:files:edit', 'File saved to {0}'.format(path))
        else:
            logger.info('ctl:files:edit', 'File not saved')
    except Exception as e:
        raise CLIException(str(e))
