# -*- coding: utf-8 -*-
import click

from utils import abort_if_false, handle_job, CLIException, ClickMessager


@click.group()
def websites():
    """Website commands"""
    pass


def _list_websites(sites):
    if not sites:
        click.echo("No websites found")
    for x in sorted(sites, key=lambda x: x["id"]):
        url = "https://" if x["certificate"] else "http://"
        url += x["addr"]
        url += (":{}".format(x["port"])) if x["port"] not in [80, 443] else ""
        click.echo(click.style(x["id"], fg="green") + click.style(" (" + url +")", fg="yellow"))
        click.secho(u" ↳ Site Type: " + x["site_name"], fg="white")
        click.secho(u" ↳ Uses SSL: {}".format("Yes" if x["certificate"] else "No"), fg="white")
        click.secho(u" ↳ Enabled: {}".format("Yes" if x["enabled"] else "No"), fg="white")


@websites.command()
@click.pass_context
def list(ctx):
    """List all websites"""
    try:
        if ctx.obj["conn_method"] == "remote":
            adata = ctx.obj["client"].websites.get()
        elif ctx.obj["conn_method"] == "local":
            from arkos import website
            adata = [x.serialized for x in websites.get()]
    except Exception, e:
        raise CLIException(str(e))
    else:
        _list_websites(adata)

@websites.command()
@click.argument("id")
@click.option("--site-type", help="Type identifier for website (see list of Apps)")
@click.option("--address", help="The domain (with subdomain) to make this site available on. Must have added via Domains")
@click.option("--port", type=int, help="The port number to make the site available on (default 80)")
@click.option("--extra-data", help="Any extra data your site might require")
@click.pass_context
def add(ctx, id, site_type, address, port, extra_data):
    """Create a website"""
    try:
        edata = {}
        if extra_data:
            for x in extra_data.split(","):
                for y in x.split("="):
                    edata[y[0]] = y[1]
        if ctx.obj["conn_method"] == "remote":
            job, data = ctx.obj["client"].websites.create(id, site_type, address, port, edata)
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            from arkos import applications, websites
            sapp = applications.get(site_type)
            site = sapp._website
            site = site(id, address, port)
            site.install(sapp, edata, True, ClickMessager())
    except Exception, e:
        raise CLIException(str(e))

@websites.command()
@click.argument("id")
@click.option("--yes", is_flag=True, callback=abort_if_false,
              expose_value=False, prompt='Are you sure you want to remove this site?')
@click.pass_context
def remove(ctx, id):
    """Remove a website"""
    try:
        if ctx.obj["conn_method"] == "remote":
            job = ctx.obj["client"].websites.delete(id)
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            from arkos import websites
            site = websites.get(id)
            site.remove(ClickMessager())
    except Exception, e:
        raise CLIException(str(e))
    else:
        click.secho("Website removed successfully.", bold=True)


GROUPS = [websites]
