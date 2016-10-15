# -*- coding: utf-8 -*-
import click

from arkosctl import client, CLIException, logger


@click.group(name='svc')
def services():
    """Service commands"""
    pass


@services.command(name='list')
def list_services():
    """List all services and statuses."""
    try:
        data = []
        svcs = client().services.get()
        llen = len(sorted(svcs, key=lambda x: len(x["id"]))[-1]["id"])
        for x in svcs:
            data.append(
                click.style(
                    '{name: <{fill}}'.format(name=x["id"], fill=llen + 3),
                    fg="white", bold=True) +
                click.style(
                    x["state"].capitalize(),
                    fg="green" if x["state"] == "running" else "red") + "   " +
                click.style(
                    "Enabled" if x["enabled"] else "Disabled",
                    fg="green" if x["enabled"] else "red")
            )
        click.echo_via_pager("\n".join(data))
    except Exception as e:
        raise CLIException(str(e))


@services.command()
@click.argument("name")
def start(name):
    """Start a service"""
    try:
        client().services.start(name)
        svc = client().services.get(id=name)
        state = svc["state"]
        if state == "running":
            logger.success('ctl:svc:start', 'Started {0}'.format(name))
        else:
            logger.error('ctl:svc:start', 'Failed to start {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@services.command()
@click.argument("name")
def stop(name):
    """Stop a service"""
    try:
        client().services.stop(name)
        logger.success('ctl:svc:stop', 'Stopped {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@services.command()
@click.argument("name")
def restart(name):
    """Restart a service"""
    try:
        svc = client().services.restart(name)
        state = svc["state"]
        if state == "running":
            logger.success('ctl:svc:restart', 'Restarted {0}'.format(name))
        else:
            logger.error(
                'ctl:svc:restart', 'Failed to restart {0}'.format(name)
            )
    except Exception as e:
        raise CLIException(str(e))


@services.command()
@click.argument("name")
def enable(name):
    """Enable a service on boot"""
    try:
        client().services.enable(name)
        logger.success('ctl:svc:enable', 'Enabled {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@services.command()
@click.argument("name")
def disable(name):
    """Disable a service on boot"""
    try:
        client().services.disable(name)
        logger.success('ctl:svc:disable', 'Disabled {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@services.command()
@click.argument("name")
def status(name):
    """Get service status"""
    try:
        svc = client().services.get(id=name)
        if not svc:
            raise CLIException("No service found")
        llen = len(svc["id"]) if len(svc["id"]) > 20 else 20
        click.echo(
            click.style(
                '{name: <{fill}}'.format(name=svc["id"], fill=llen + 3),
                fg="white", bold=True) +
            click.style(
                svc["state"].capitalize(),
                fg="green" if svc["state"] == "running" else "red") + "   " +
            click.style(
                "Enabled" if svc["enabled"] else "Disabled",
                fg="green" if svc["enabled"] else "red")
        )
    except Exception as e:
        raise CLIException(str(e))
