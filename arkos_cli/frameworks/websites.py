# -*- coding: utf-8 -*-
import click

from arkos_cli.utils import u, AliasedGroup, abort_if_false, handle_job, CLIException, ClickMessager


@click.command(cls=AliasedGroup)
def websites():
    """Website commands"""
    pass


def _list_websites(sites):
    if not sites:
        click.echo("No websites found")
    for x in sorted(sites, key=lambda x: x["id"]):
        url = "https://" if x["certificate"] else "http://"
        url += x["addr"]
        url += (":{0}".format(x["port"])) if x["port"] not in [80, 443] else ""
        click.echo(click.style(x["id"], fg="green") + click.style(" (" + url +")", fg="yellow"))
        click.secho(u(" ↳ Site Type: ") + x["site_name"], fg="white")
        click.secho(u(" ↳ Uses SSL: {0}").format("Yes" if x["certificate"] else "No"), fg="white")
        click.secho(u(" ↳ Enabled: {0}").format("Yes" if x["enabled"] else "No"), fg="white")
        if x.get("has_update"):
            click.secho(u(" ↳ Update available!"), fg="green")


@websites.command()
@click.pass_context
def list(ctx):
    """List all websites"""
    try:
        if ctx.obj["conn_method"] == "remote":
            adata = ctx.obj["client"].websites.get()
        elif ctx.obj["conn_method"] == "local":
            from arkos import websites
            adata = [x.serialized for x in websites.get()]
    except Exception as e:
        raise CLIException(str(e))
    else:
        _list_websites(adata)

@websites.command()
@click.argument("id")
@click.option("--site-type", prompt=True, help="Type identifier for website (see list of Apps)")
@click.option("--address", prompt=True, help="The domain (with subdomain) to make this site available on. Must have added via Domains")
@click.option("--port", prompt=True, type=int, help="The port number to make the site available on (default 80)")
@click.option("--extra-data", help="Any extra data your site might require")
@click.pass_context
def add(ctx, id, site_type, address, port, extra_data):
    """Create a website"""
    try:
        edata = {}
        if extra_data:
            for x in extra_data.split(","):
                edata[x.split("=")[0]] = x.split("=")[1]
        if ctx.obj["conn_method"] == "remote":
            stype = ctx.obj["client"].applications.get(id=site_type.lower())
            if stype.get("website_options") and not extra_data:
                for x in stype["website_options"]:
                    edata[x["id"]] = click.prompt(x["name"])
            job, data = ctx.obj["client"].websites.create(id, site_type.lower(), address, port, edata)
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            from arkos import applications, websites
            sapp = applications.get(site_type.lower())
            if hasattr(sapp, "website_options") and not extra_data:
                for x in sapp.website_options:
                    edata[x["id"]] = click.prompt(x["name"])
            site = sapp._website
            site = site(id, address, port)
            site.install(sapp, edata, True, ClickMessager())
    except Exception as e:
        raise CLIException(str(e))

@websites.command()
@click.argument("id")
@click.option("--address", help="The domain (with subdomain) to make this site available on. Must have added via Domains")
@click.option("--port", type=int, help="The port number to make the site available on (default 80)")
@click.option("--new_name", default="", help="Any extra data your site might require")
@click.pass_context
def edit(ctx, id, address, port, new_name):
    """Edit a website"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].websites.edit(id, new_name, address, port)
        elif ctx.obj["conn_method"] == "local":
            from arkos import websites
            site = websites.get(id)
            site.addr = address
            site.port = port
            site.edit(new_name or None)
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Site edited successfully.", fg="green")

@websites.command()
@click.argument("id")
@click.pass_context
def enable(ctx, id):
    """Enable a website"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].websites.enable(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos import websites
            site = websites.get(id)
            site.nginx_enable()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Site enabled.", fg="green")

@websites.command()
@click.argument("id")
@click.pass_context
def disable(ctx, id):
    """Disable a website"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].websites.disable(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos import websites
            site = websites.get(id)
            site.nginx_disable()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Site disabled.", fg="red")

@websites.command()
@click.argument("id")
@click.pass_context
def update(ctx, id):
    """Update a website"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].websites.update(id)
        elif ctx.obj["conn_method"] == "local":
            from arkos import websites
            site = websites.get(id)
            site.update()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Site updated successfully.", fg="green")

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
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Website removed successfully.", bold=True)


list.aliases = ["websites", "sites"]
add.aliases = ["create", "install"]
edit.aliases = ["change"]
update.aliases = ["upgrade"]
remove.aliases = ["delete"]
GROUPS = [[websites, "website", "sites", "site", "web"]]
