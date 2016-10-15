# -*- coding: utf-8 -*-
"""Relates to commands for management of databases."""
import click

from arkosctl import client, CLIException, logger


@click.group()
def db():
    """Database commands."""
    pass


@click.group(name='dbuser')
def db_users():
    """Database user commands."""
    pass


@db.command(name='list')
def list_dbs():
    """List all databases."""
    try:
        dbs = client().databases.get()
        if not dbs:
            logger.info('ctl:db:list', 'No databases found')
        llen = len(sorted(dbs, key=lambda x: len(x["id"]))[-1]["id"])
        for x in sorted(dbs, key=lambda x: x["id"]):
            click.echo(
                click.style(
                    '{name: <{fill}}'.format(name=x["id"], fill=llen + 3),
                    fg="white", bold=True) +
                click.style(
                    client().databases.get_types(
                        id=x["database_type"])["name"],
                    fg="yellow")
            )
    except Exception as e:
        raise CLIException(str(e))


@db_users.command(name='list')
def list_users():
    """List all database users."""
    try:
        dbs = client().databases.get_users()
        if not dbs:
            logger.info('ctl:dbusr:list', 'No database users found')
            return
        llen = len(sorted(dbs, key=lambda x: len(x["id"]))[-1]["id"])
        for x in sorted(dbs, key=lambda x: x["id"]):
            click.echo(
                click.style(
                    '{name: <{fill}}'.format(name=x["id"], fill=llen + 3),
                    fg="white", bold=True) +
                click.style(
                    client().databases.get_types(
                        id=x["database_type"])["name"],
                    fg="yellow")
            )
    except Exception as e:
        raise CLIException(str(e))


@db.command(name='types')
def list_types():
    """List all database types and running status."""
    try:
        dbs = client().databases.get_types()
        if not dbs:
            logger.info('ctl:db:types', 'No databases found')
            return
        llen = len(sorted(dbs, key=lambda x: len(x["name"]))[-1]["name"])
        for x in sorted(dbs, key=lambda x: x["id"]):
            click.echo(
                click.style(
                    '{name: <{fill}}'.format(name=x["name"], fill=llen + 3),
                    fg="white", bold=True) +
                click.style(
                    "Running" if x["state"] else "Stopped",
                    fg="green" if x["state"] else "red")
            )
    except Exception as e:
        raise CLIException(str(e))


@db.command(name='create')
@click.argument("name")
@click.argument("type_id")
def add(name, type_id):
    """Add a database."""
    try:
        client().databases.add(name, "db-" + type_id)
        logger.success('ctl:db:create', 'Added {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@db_users.command(name='add')
@click.argument("name")
@click.argument("type_id")
def add_user(name, type_id):
    """Add a database user."""
    try:
        client().databases.add_user(name, type_id)
        logger.success('ctl:dbusr:add', 'Added user {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@db.command()
@click.argument("name")
@click.argument("path", type=click.File("wb"))
def dump(name, path):
    """Export database to SQL file."""
    try:
        data = client().databases.dump(name)
        path.write(data)
        logger.success('ctl:db:dump', 'Database dumped to {0}'.format(path))
    except Exception as e:
        raise CLIException(str(e))


@db_users.command()
@click.argument("user_name")
@click.argument("db_name")
@click.option("--grant/revoke", required=True,
              help="Grant or revoke all access to this DB with this user")
def chmod(user_name, db_name, grant):
    """Get or set database user permissions."""
    try:
        cmd = client().databases.user_chmod
        cmd(user_name, "grant" if grant else "revoke")
        logger.success('ctl:dbusr:chmod', 'Permissions set')
    except Exception as e:
        raise CLIException(str(e))


@db.command()
@click.argument("name")
def drop(name):
    """Delete a database."""
    try:
        client().databases.delete(name)
        logger.success('ctl:db:drop', 'Dropped {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@db_users.command(name='drop')
@click.argument("name")
def drop_user(name):
    """Delete a database user."""
    try:
        client().databases.delete_user(name)
        logger.success('ctl:dbusr:drop', 'Dropped {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))
