# -*- coding: utf-8 -*-
"""Relates to commands for management of applications."""
import click

from arkosctl import client, CLIException, logger
from arkosctl.utils import abort_if_false, handle_job


@click.group(name='app')
def applications():
    """Application commands."""
    pass


def _list_applications(apps):
    if not apps:
        logger.info('ctl:app:list', 'No apps found')
        return
    nlen = len(sorted(apps, key=lambda x: len(x["name"]))[-1]["name"])
    vlen = len(sorted(apps, key=lambda x: len(x["version"]))[-1]["version"])
    for x in sorted(apps, key=lambda x: x["name"]):
        click.echo(
            click.style(
                '{name: <{fill}}'.format(name=x["name"], fill=nlen + 3),
                fg="white", bold=True) +
            click.style(
                '{name: <{fill}}'.format(name=x["version"], fill=vlen + 3),
                fg="green") + "   " +
            x["description"]["short"]
        )


@applications.command(name='list')
@click.option("--show-hidden", is_flag=True,
              help="Show hidden apps too (like databases)")
def list_apps(show_hidden):
    """List all applications."""
    try:
        adata = client().applications.get()
        if not show_hidden:
            adata = [x for x in adata if x["type"] not in ["database"]]
        _list_applications(adata)
    except Exception as e:
        raise CLIException(str(e))


@applications.command()
@click.option("--show-hidden", is_flag=True,
              help="Show hidden apps too (like databases)")
def installed(show_hidden):
    """List all installed applications."""
    try:
        adata = client().applications.get(installed=True)
        if not show_hidden:
            adata = [x for x in adata if x["type"] not in ["database"]]
        _list_applications(adata)
    except Exception as e:
        raise CLIException(str(e))


@applications.command()
@click.option("--show-hidden", is_flag=True,
              help="Show hidden apps too (like databases)")
def available(show_hidden):
    """List all available applications."""
    try:
        adata = client().applications.get(installed=False)
        if not show_hidden:
            adata = [x for x in adata if x["type"] not in ["database"]]
        _list_applications(adata)
    except Exception as e:
        raise CLIException(str(e))


@applications.command()
@click.argument("id")
def info(id):
    """Get information about a certain application."""
    try:
        x = client().applications.get(id=id)
        lines = {
            "Type:": x["type"].capitalize(),
            "By:": x["app_author"],
            "Description:": x["description"]["short"],
            "Website:": x["app_homepage"],
            "Installed:": "Yes" if x["installed"] else "No"
        }
        click.echo(click.style(x["name"], fg="white", bold=True))
        click.echo(click.style(" * Version: ", fg="yellow") + x["version"])
        if x["upgradable"]:
            click.echo(
                click.style(" * Upgradable to: ", fg="green") + x["upgradable"]
            )
        for key in sorted(lines.keys()):
            imsg = click.style(lines[key], fg="white")
            click.echo(click.style(" * " + key, fg="yellow") + " " + imsg)
        if [y for y in x["dependencies"] if y["type"] == "app"]:
            deps = [y["name"] for y in x["dependencies"] if y["type"] == "app"]
            click.echo(click.style(" * Depends on:", fg="yellow") +
                       " " + click.style(", ".join(deps), fg="white"))
    except Exception as e:
        raise CLIException(str(e))


@applications.command()
@click.argument("id")
def install(id):
    """Install an application."""
    try:
        job, data = client().applications.install(id=id)
        handle_job(job)
    except Exception as e:
        raise CLIException(str(e))


@applications.command()
@click.argument("id")
@click.option("--yes", callback=abort_if_false, expose_value=False,
              is_flag=True, prompt='Are you sure you want to remove this app?')
def uninstall(id):
    """Uninstall an application."""
    try:
        job, data = client().applications.uninstall(id=id)
        handle_job(job)
    except Exception as e:
        raise CLIException(str(e))
