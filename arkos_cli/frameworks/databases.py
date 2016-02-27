# -*- coding: utf-8 -*-
import click

from utils import AliasedGroup, CLIException


@click.command(cls=AliasedGroup)
def databases():
    """Database commands"""
    pass


@databases.command()
@click.pass_context
def list(ctx):
    """List all databases"""
    try:
        if ctx.obj["conn_method"] == "remote":
            dbs = ctx.obj["client"].databases.get()
        elif ctx.obj["conn_method"] == "local":
            from arkos import databases
            dbs = [x.as_dict for x in databases.get()]
    except Exception, e:
        raise CLIException(str(e))
    else:
        if not dbs:
            click.secho("No databases found", bold=True)
        for x in sorted(dbs, key=lambda x: x["id"]):
            click.echo(click.style(x["id"], fg="green") + click.style(" (" + x["type_name"] +")", fg="yellow"))

@databases.command()
@click.pass_context
def list_users(ctx):
    """List all database users"""
    try:
        if ctx.obj["conn_method"] == "remote":
            dbs = ctx.obj["client"].databases.get_users()
        elif ctx.obj["conn_method"] == "local":
            from arkos import databases
            dbs = [x.as_dict for x in databases.get_users()]
    except Exception, e:
        raise CLIException(str(e))
    else:
        if not dbs:
            click.secho("No database users found", bold=True)
        for x in sorted(dbs, key=lambda x: x["id"]):
            click.echo(click.style(x["id"], fg="green") + click.style(" (" + x["type_name"] +")", fg="yellow"))

@databases.command()
@click.pass_context
def list_types(ctx):
    """List all database types and running status"""
    try:
        if ctx.obj["conn_method"] == "remote":
            dbs = ctx.obj["client"].databases.get_types()
        elif ctx.obj["conn_method"] == "local":
            from arkos import databases
            dbs = [x.as_dict for x in databases.get_managers()]
    except Exception, e:
        raise CLIException(str(e))
    else:
        if not dbs:
            click.secho("No database types found", bold=True)
        for x in sorted(dbs, key=lambda x: x["id"]):
            click.echo(click.style(x["name"], fg="green") + click.style(" (Running)" if x["state"] else " (Stopped)", fg="yellow"))

@databases.command()
@click.argument("name")
@click.argument("type_id")
@click.pass_context
def add(ctx, name, type_id):
    """Add a database"""
    click.secho("Adding database...", fg="green")
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].databases.add(name, "db-" + type_id)
        elif ctx.obj["conn_method"] == "local":
            from arkos import databases
            manager = databases.get_managers("db-" + type_id)
            manager.add_db(name)
    except Exception, e:
        raise CLIException(str(e))
    else:
        click.secho("Database added!", fg="yellow")

@databases.command()
@click.argument("name")
@click.argument("type_id")
@click.pass_context
def add_user(ctx, name, type_id):
    """Add a database user"""
    click.secho("Adding database user...", fg="green")
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].databases.add_user(name, type_id)
        elif ctx.obj["conn_method"] == "local":
            from arkos import databases
            manager = databases.get_managers("db-" + type_id)
            manager.add_user(name)
    except Exception, e:
        raise CLIException(str(e))
    else:
        click.secho("Database user added!", fg="yellow")

@databases.command()
@click.argument("name")
@click.argument("path", type=click.File("wb"))
@click.pass_context
def dump(ctx, name, path):
    """Export database to SQL file"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].databases.dump(name)
        elif ctx.obj["conn_method"] == "local":
            from arkos import databases
            db = databases.get(name)
            data = db.dump()
        path.write(data)
    except Exception, e:
        raise CLIException(str(e))
    else:
        click.echo("Database saved to {}".format(path))

@databases.command()
@click.argument("user_name")
@click.argument("db_name")
@click.option("--grant/revoke", required=True, help="Grant or revoke all access to this DB with this user")
@click.pass_context
def chmod(ctx, user_name, db_name, grant):
    """Gets or sets database user permissions"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].databases.user_chmod(user_name, "grant" if grant else "revoke")
        elif ctx.obj["conn_method"] == "local":
            from arkos import databases
            u = databases.get_user(user_name)
            u.chperm("grant" if grant else "revoke", databases.get(db_name))
    except Exception, e:
        raise CLIException(str(e))
    else:
        click.echo("Database permissions set.")

@databases.command()
@click.argument("name")
@click.pass_context
def drop(ctx, name):
    """Deletes a database"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].databases.delete(name)
        elif ctx.obj["conn_method"] == "local":
            from arkos import databases
            db = databases.get(name)
            db.remove()
    except Exception, e:
        raise CLIException(str(e))
    else:
        click.echo("Database dropped.")

@databases.command()
@click.argument("name")
@click.pass_context
def drop_user(ctx, name):
    """Deletes a database user"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].databases.delete_user(name)
        elif ctx.obj["conn_method"] == "local":
            from arkos import databases
            u = databases.get_user(name)
            u.remove()
    except Exception, e:
        raise CLIException(str(e))
    else:
        click.echo("Database user dropped.")


list.aliases = ["dbs"]
list_users.aliases = ["list-users", "users"]
list_types.aliases = ["list-types", "types", "engines"]
add.aliases = ["create", "new"]
add_user.aliases = ["add-user", "create-user", "new-user"]
dump.aliases = ["export", "backup"]
chmod.aliases = ["permissions", "perms"]
drop.aliases = ["remove", "delete"]
drop_user.aliases = ["drop-user", "remove-user", "delete-user"]
GROUPS = [[databases, "database", "dbs", "db"]]
