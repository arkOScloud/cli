# -*- coding: utf-8 -*-
import click

from arkosctl import client, CLIException, logger
from arkosctl.utils import abort_if_false, handle_job


@click.group(name='sites')
def websites():
    """Website commands"""
    pass


def _list_websites(sites):
    if not sites:
        logger.info('ctl:site:list', 'No websites found')
    for x in sorted(sites, key=lambda x: x["id"]):
        url = "https://" if x["certificate"] else "http://"
        url += x["domain"]
        url += (":{0}".format(x["port"])) if x["port"] not in [80, 443] else ""
        click.echo(click.style(x["id"], fg="green", bold=True))
        click.echo(click.style(" * URL: ", fg="yellow") + url)
        click.echo(click.style(" * Site Type: ", fg="yellow") + x["app_name"])
        click.echo(
            click.style(" * Uses SSL: ", fg="yellow") +
            ("Yes" if x["certificate"] else "No")
        )
        click.echo(
            click.style(" * Enabled: ", fg="yellow") +
            ("Yes" if x["enabled"] else "No")
        )
        if x.get("has_update"):
            click.secho(" * Update available!", fg="green")


@websites.command(name='list')
def list_sites():
    """List all websites"""
    try:
        adata = client().websites.get()
        _list_websites(adata)
    except Exception as e:
        raise CLIException(str(e))


@websites.command()
@click.argument("id")
@click.option(
    "--site-type", prompt=True,
    help="Type identifier for website (see list of Apps)")
@click.option(
    "--address", prompt=True,
    help="The domain (with subdomain) to make this site available on. "
    "Must have added via Domains")
@click.option(
    "--port", prompt=True, type=int,
    help="The port number to make the site available on (default 80)")
@click.option("--extra-data", help="Any extra data your site might require")
def create(id, site_type, address, port, extra_data):
    """Create a website"""
    try:
        edata = {}
        if extra_data:
            for x in extra_data.split(","):
                edata[x.split("=")[0]] = x.split("=")[1]
        stype = client().applications.get(id=site_type.lower())
        if stype.get("website_options") and not extra_data:
            for x in stype["website_options"]:
                if x == "messages":
                    continue
                for y in stype["website_options"][x]:
                    edata[y["id"]] = click.prompt(y["label"])
        job, data = client().websites.create(
            id, site_type.lower(), address, port, edata)
        handle_job(job)
    except Exception as e:
        raise CLIException(str(e))


@websites.command()
@click.argument("id")
@click.option(
    "--address",
    help="The domain (with subdomain) to make this site available on. "
    "Must have added via Domains")
@click.option(
    "--port", type=int,
    help="The port number to make the site available on (default 80)")
@click.option(
    "--new_name", default="", help="Any extra data your site might require")
def edit(id, address, port, new_name):
    """Edit a website"""
    try:
        client().websites.edit(id, new_name, address, port)
        logger.success('ctl:site:edit', 'Edited {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@websites.command()
@click.argument("id")
def enable(id):
    """Enable a website"""
    try:
        client().websites.enable(id)
        logger.success('ctl:site:enable', 'Enabled {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@websites.command()
@click.argument("id")
def disable(id):
    """Disable a website"""
    try:
        client().websites.disable(id)
        logger.success('ctl:site:disable', 'Disabled {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@websites.command()
@click.argument("id")
def update(id):
    """Update a website"""
    try:
        client().websites.update(id)
        logger.success('ctl:site:update', 'Updated {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@websites.command()
@click.argument("id")
@click.option(
    "--yes", is_flag=True, callback=abort_if_false, expose_value=False,
    prompt='Are you sure you want to remove this site?')
def remove(id):
    """Remove a website"""
    try:
        job = client().websites.delete(id)
        handle_job(job)
    except Exception as e:
        raise CLIException(str(e))
