# -*- coding: utf-8 -*-
import click

from arkosctl import client, CLIException, logger


@click.group(name='sec')
def security():
    """Security commands"""
    pass


@security.command()
def list():
    """List security policies"""
    try:
        data = client().security.get_policies()
        for x in data:
            pol, fg = ("Allow All", "green") if x["policy"] == 2 else \
                (("Local Only", "yellow") if x["policy"] == 1 else
                    ("Restricted", "red"))
            click.echo(
                click.style(x["name"], fg="white", bold=True) +
                click.style(" (" + x["id"] + ")", fg="green")
            )
            click.echo(click.style(" * Type: ", fg="yellow") + x["type"])
            click.echo(
                click.style(" * Ports: ", fg="yellow") +
                ", ".join(
                    ["{0} {1}".format(y[1], y[0].upper()) for y in x["ports"]]
                )
            )
            click.echo(
                click.style(" * Policy: ", fg="yellow") +
                click.style(pol, fg=fg)
            )
    except Exception as e:
        raise CLIException(str(e))


@security.command()
@click.argument("id")
def allow(id):
    """Allow all access to service"""
    try:
        client().security.update_policy(id, "allow")
        logger.success('ctl:sec:allow', 'Access to {0} allowed'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@security.command()
@click.argument("id")
def local(id):
    """Allow local network access only to service"""
    try:
        client().security.update_policy(id, "local")
        logger.success('ctl:sec:local', 'Access to {0} restricted'.format(id))
    except Exception as e:
        raise CLIException(str(e))


@security.command()
@click.argument("id")
def block(id):
    """Block all network access to service"""
    try:
        client().security.update_policy(id, "block")
        logger.success('ctl:sec:block', 'Access to {0} blocked'.format(id))
    except Exception as e:
        raise CLIException(str(e))
