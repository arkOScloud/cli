# -*- coding: utf-8 -*-
import click

from arkosctl import client, CLIException, logger
from arkosctl.utils import abort_if_false, handle_job


@click.group(name='pkg')
def packages():
    """System package commands"""
    pass


@packages.command()
@click.argument("name", required=True, nargs=-1)
@click.option(
    "--yes", is_flag=True, callback=abort_if_false, expose_value=False,
    prompt='Are you sure you want to install these packages?')
def install(name):
    """Install system package(s)"""
    try:
        job = client().packages.install(name)
        handle_job(job)
    except Exception as e:
        raise CLIException(str(e))


@packages.command()
@click.argument("name", required=True, nargs=-1)
@click.option(
    "--purge", is_flag=True, help="Purge associated files and folders")
@click.option(
    "--yes", is_flag=True, callback=abort_if_false, expose_value=False,
    prompt='Are you sure you want to remove these packages?')
def remove(name, purge):
    """Removes system package(s)"""
    try:
        job = client().packages.remove(name)
        handle_job(job)
    except Exception as e:
        raise CLIException(str(e))


@packages.command()
def update():
    """Updates system package index"""
    try:
        client().packages.get(refresh=True)
        logger.success('ctl:pkg:update', 'Index updated')
    except Exception as e:
        raise CLIException(str(e))


@packages.command()
@click.option("--yes", is_flag=True)
def upgrade(yes):
    """Upgrades all system packages"""
    try:
        pkgs = client().packages.get(refresh=False)
        pkgs = [x["id"] for x in pkgs if x["upgradable"]]
        if not pkgs:
            logger.info('ctl:pkg:upgrade', 'System already up-to-date')
        else:
            logger.info(
                'ctl:pkg:upgrade', 'The following packages will be upgraded:'
            )
            click.echo(", ".join(pkgs))
            if yes or click.confirm("Are you sure you want to upgrade?"):
                job = client().packages.install(pkgs)
                handle_job(job)
    except Exception as e:
        raise CLIException(str(e))
