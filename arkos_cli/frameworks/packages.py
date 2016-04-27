# -*- coding: utf-8 -*-
import click

from arkos_cli.utils import AliasedGroup, abort_if_false, handle_job, CLIException


@click.command(cls=AliasedGroup)
def packages():
    """System package commands"""
    pass

@packages.command()
@click.argument("name", required=True, nargs=-1)
@click.option("--yes", is_flag=True, callback=abort_if_false,
              expose_value=False, prompt='Are you sure you want to install these packages?')
@click.pass_context
def install(ctx, name):
    """Install system package(s)"""
    try:
        if ctx.obj["conn_method"] == "remote":
            job = ctx.obj["client"].packages.install(name)
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            import pacman
            click.echo("Installing {}...".format(", ".join(name)))
            pacman.install(list(name))
            click.secho("Operation completed successfully", fg="green")
    except Exception as e:
        raise CLIException(str(e))

@packages.command()
@click.argument("name", required=True, nargs=-1)
@click.option("--purge", is_flag=True, help="Purge associated files and folders")
@click.option("--yes", is_flag=True, callback=abort_if_false,
              expose_value=False, prompt='Are you sure you want to remove these packages?')
@click.pass_context
def remove(ctx, name, purge):
    """Removes system package(s)"""
    try:
        if ctx.obj["conn_method"] == "remote":
            job = ctx.obj["client"].packages.remove(name)
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            import pacman
            click.echo("Removing {}...".format(", ".join(name)))
            pacman.remove(list(name), purge=purge)
            click.secho("Operation completed successfully", fg="green")
    except Exception as e:
        raise CLIException(str(e))

@packages.command()
@click.pass_context
def update(ctx):
    """Updates system package index"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].packages.get(refresh=True)
        elif ctx.obj["conn_method"] == "local":
            import pacman
            pacman.refresh()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Operation completed successfully", fg="green")

@packages.command()
@click.option("--yes", is_flag=True)
@click.pass_context
def upgrade(ctx, yes):
    """Upgrades all system packages"""
    try:
        if ctx.obj["conn_method"] == "remote":
            pkgs = ctx.obj["client"].packages.get(refresh=False)
            pkgs = [x["id"] for x in pkgs if x["upgradable"]]
            if not pkgs:
                click.echo("System already up-to-date")
            else:
                click.echo(click.style("The following packages will be upgraded: ", bold=True) + ", ".join(pkgs))
                if yes or click.confirm("Are you sure you want to upgrade?"):
                    job = ctx.obj["client"].packages.install(pkgs)
                    handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            import pacman
            pkgs = pacman.get_installed()
            pkgs = [x["id"] for x in pkgs if x["upgradable"]]
            if not pkgs:
                click.echo("System already up-to-date")
            else:
                click.echo(click.style("The following packages will be upgraded: ", bold=True) + ", ".join(pkgs))
                if yes or click.confirm("Are you sure you want to upgrade?"):
                    click.echo("Upgrading system...")
                    pacman.upgrade()
                    click.secho("Operation completed successfully", fg="green")
    except Exception as e:
        raise CLIException(str(e))


remove.aliases = ["uninstall"]
update.aliases = ["sync"]
GROUPS = [[packages, "package", "pkg"]]
