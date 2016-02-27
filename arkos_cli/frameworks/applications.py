# -*- coding: utf-8 -*-
import click

from utils import abort_if_false, handle_job, CLIException, ClickMessager


@click.group()
def applications():
    """Applications commands"""
    pass


def _list_applications(apps):
    if not apps:
        click.echo("No applications found")
    for x in sorted(apps, key=lambda x: x["name"]):
        click.echo(click.style(x["name"], fg="green") + click.style(" (" + x["version"] +")", fg="yellow"))
        click.secho(u" ↳ " + x["description"]["short"], fg="white")


@applications.command()
@click.option("--show-hidden", is_flag=True, help="Show hidden apps too (like databases)")
@click.pass_context
def list(ctx, show_hidden):
    """List all applications"""
    try:
        if ctx.obj["conn_method"] == "remote":
            adata = ctx.obj["client"].applications.get()
        elif ctx.obj["conn_method"] == "local":
            from arkos import applications
            adata = [x.as_dict for x in applications.get()]
    except Exception, e:
        raise CLIException(str(e))
    else:
        if not show_hidden:
            adata = [x for x in adata if x["type"] in ["app", "website"]]
        _list_applications(adata)

@applications.command()
@click.option("--show-hidden", is_flag=True, help="Show hidden apps too (like databases)")
@click.pass_context
def installed(ctx):
    """List all installed applications"""
    try:
        if ctx.obj["conn_method"] == "remote":
            adata = ctx.obj["client"].applications.get(installed=True)
        elif ctx.obj["conn_method"] == "local":
            from arkos import applications
            adata = [x.as_dict for x in applications.get(installed=True)]
    except Exception, e:
        raise CLIException(str(e))
    else:
        if not show_hidden:
            adata = [x for x in adata if x["type"] in ["app", "website"]]
        _list_applications(adata)

@applications.command()
@click.option("--show-hidden", is_flag=True, help="Show hidden apps too (like databases)")
@click.pass_context
def available(ctx):
    """List all available applications"""
    try:
        if ctx.obj["conn_method"] == "remote":
            adata = ctx.obj["client"].applications.get(installed=False)
        elif ctx.obj["conn_method"] == "local":
            from arkos import applications
            adata = [x.as_dict for x in applications.get(installed=False)]
    except Exception, e:
        raise CLIException(str(e))
    else:
        if not show_hidden:
            adata = [x for x in adata if x["type"] in ["app", "website"]]
        _list_applications(adata)

@applications.command()
@click.argument("id")
@click.pass_context
def info(ctx, id):
    """Get information about a certain application"""
    try:
        if ctx.obj["conn_method"] == "remote":
            x = ctx.obj["client"].applications.get(id=id)
        elif ctx.obj["conn_method"] == "local":
            from arkos import applications
            x = applications.get(id).as_dict
    except Exception, e:
        raise CLIException(str(e))
    else:
        lines = {
            "Type:": x["type"].capitalize(),
            "By:": x["app_author"],
            "Description:": x["description"]["short"],
            "Website:": x["app_homepage"],
            "Installed:": "Yes" if x["installed"] else "No"
        }
        click.echo(click.style(x["name"], fg="green") + click.style(" (" + x["version"] +")", fg="yellow"))
        for key in sorted(lines.keys()):
            click.echo(u" ↳ " + click.style(key, fg="yellow") + " " + click.style(lines[key], fg="white"))
        if [y for y in x["dependencies"] if y["type"] == "app"]:
            click.echo(u" ↳ " + click.style("Depends on:", fg="yellow") + " " + click.style(", ".join([y["name"] for y in x["dependencies"] if y["type"] == "app"]), fg="white"))

@applications.command()
@click.argument("id")
@click.pass_context
def install(ctx, id):
    """Install an application"""
    try:
        if ctx.obj["conn_method"] == "remote":
            job, data = ctx.obj["client"].applications.install(id=id)
            click.secho("Installing application {}...".format(data["name"]), fg="green")
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            from arkos import applications
            applications.get(id).install(message=ClickMessager(), force=True)
    except Exception, e:
        raise CLIException(str(e))
    else:
        click.secho("Application installed successfully.", bold=True)

@applications.command()
@click.argument("id")
@click.option("--yes", is_flag=True, callback=abort_if_false,
              expose_value=False, prompt='Are you sure you want to remove this app?')
@click.pass_context
def uninstall(ctx, id):
    """Uninstall an application"""
    try:
        if ctx.obj["conn_method"] == "remote":
            job, data = ctx.obj["client"].applications.uninstall(id=id)
            click.secho("Uninstalling application {}...".format(data["name"]), fg="green")
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            from arkos import applications
            applications.get(id).uninstall(message=ClickMessager())
    except Exception, e:
        raise CLIException(str(e))
    else:
        click.secho("Application uninstalled successfully.", bold=True)


GROUPS = [[applications, "application", "app", "apps"]]
