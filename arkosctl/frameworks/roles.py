# -*- coding: utf-8 -*-
import click

from arkosctl import client, CLIException, logger
from arkosctl.utils import abort_if_false


@click.group()
def user():
    """User commands (LDAP)"""
    pass


@click.group()
def group():
    """Group commands (LDAP)"""
    pass


@click.group()
def domain():
    """Domain commands (LDAP)"""
    pass


@user.command(name='list')
def list_users():
    """List users"""
    try:
        data = client().roles.get_users()
        for x in data:
            click.echo(
                click.style(x["name"], fg="white", bold=True) +
                click.style(" ({0})".format(x["id"]), fg="green")
            )
            click.echo(
                click.style(" * Name: ", fg="yellow") +
                x["first_name"] +
                (" " + x["last_name"] if x["last_name"] else "")
            )
            click.echo(
                click.style(" * Mail Addresses: ", fg="yellow") +
                ", ".join(x["mail_addresses"])
            )
            click.echo(
                click.style(" * Types: ", fg="yellow") +
                ", ".join([
                    y for y in [
                        "sudo" if x["sudo"] else None,
                        "admin" if x["admin"] else None
                    ] if y
                ])
            )
    except Exception as e:
        raise CLIException(str(e))


@user.command(name='add')
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True,
              confirmation_prompt=True, help="Password for new user")
@click.option(
    "--domain", prompt=True, help="Domain name to assign the new user to")
@click.option(
    "--first-name", prompt="First name or pseudonym",
    help="First name or pseudonym")
@click.option(
    "--last-name", prompt="Last name (optional)", help="Last name (optional)")
@click.option(
    "--admin", is_flag=True, prompt="Give the user admin privileges?",
    help="Give the user admin privileges?")
@click.option(
    "--sudo", is_flag=True,
    prompt="Give the user command-line sudo privileges?",
    help="Give the user command-line sudo privileges?")
def add_user(name, password, domain, first_name, last_name, admin, sudo):
    """Add a user to arkOS LDAP"""
    try:
        client().roles.add_user(
            name, password, domain, first_name, last_name, admin, sudo)
        logger.success('ctl:usr:add', 'Added {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@user.command(name='mod')
@click.argument("name")
@click.option(
    "--domain", default=None, help="Domain name to assign the new user to")
@click.option("--first-name", default=None, help="First name or pseudonym")
@click.option("--last-name", default=None, help="Last name (optional)")
@click.option(
    "--admin", is_flag=True, default=None,
    help="Give the user admin privileges?")
@click.option(
    "--sudo", is_flag=True, default=None,
    help="Give the user command-line sudo privileges?")
def mod_user(name, domain, first_name, last_name, admin, sudo):
    """Edit an arkOS LDAP user"""
    try:
        users = client().roles.get_users()
        uid = [y["id"] for y in users if y["name"] == name]
        if not uid:
            raise CLIException("No such user")
        uid = uid[0]
        client().roles.edit_user(
            uid, domain, first_name, last_name, "", admin, sudo)
        logger.success('ctl:usr:mod', 'Modified {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@user.command()
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True,
              confirmation_prompt=True, help="Password for new user")
def passwd(name, password):
    """Change an arkOS LDAP user password"""
    try:
        users = client().roles.get_users()
        uid = [y["id"] for y in users if y["name"] == name]
        if not uid:
            raise CLIException("No such user")
        uid = uid[0]
        client().roles.edit_user(uid, passwd=password)
        logger.success(
            'ctl:usr:passwd', 'Password changed for {0}'.format(name)
        )
    except Exception as e:
        raise CLIException(str(e))


@user.command(name='delete')
@click.argument("name")
@click.option(
    "--yes", is_flag=True, callback=abort_if_false, expose_value=False,
    prompt='Are you sure you want to remove this user?')
def delete_user(name):
    """Delete an arkOS LDAP user"""
    try:
        users = client().roles.get_users()
        uid = [y["id"] for y in users if y["name"] == name]
        if not uid:
            raise CLIException("No such user")
        uid = uid[0]
        client().roles.delete_user(uid)
        logger.success('ctl:usr:delete', 'Deleted {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@group.command(name='list')
def list_groups():
    """List groups"""
    try:
        data = client().roles.get_groups()
        for x in data:
            click.echo(
                click.style(x["name"], fg="white", bold=True) +
                click.style(" ({0})".format(x["id"]), fg="green")
            )
            click.echo(
                click.style(" * Members: ", fg="yellow") +
                ", ".join(x["users"])
            )
    except Exception as e:
        raise CLIException(str(e))


@group.command(name='add')
@click.argument("name")
@click.option("--users", multiple=True)
def add_group(name, users):
    """Add a group to arkOS LDAP"""
    try:
        client().roles.add_group(name, users)
        logger.success('ctl:grp:add', 'Added {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@group.command(name='mod')
@click.argument("name")
@click.argument("operation", type=click.Choice(["add", "remove"]))
@click.argument("username")
def mod_group(name, operation, username):
    """Add/remove users from an arkOS LDAP group"""
    try:
        groups = client().roles.get_groups()
        gid = [y for y in groups if y["name"] == name]
        if not gid:
            raise CLIException("No such group")
        gid, members = gid[0]["id"], gid[0]["members"]
        if operation == "add":
            members.append(username)
        else:
            members.remove(username)
        client().roles.edit_group(gid, members)
        logger.success('ctl:grp:mod', 'Modified {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@group.command(name='delete')
@click.argument("name")
@click.option(
    "--yes", is_flag=True, callback=abort_if_false, expose_value=False,
    prompt='Are you sure you want to remove this group?')
def delete_group(name):
    """Delete an arkOS LDAP group"""
    try:
        groups = client().roles.get_groups()
        gid = [y["id"] for y in groups if y["name"] == name]
        if not gid:
            raise CLIException("No such group")
        gid = gid[0]
        client().roles.delete_group(gid)
        logger.success('ctl:grp:delete', 'Deleted {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@domain.command(name='list')
def list_domains():
    """List domains"""
    try:
        data = client().roles.get_domains()
        for x in data:
            click.echo(x["id"])
    except Exception as e:
        raise CLIException(str(e))


@domain.command(name='add')
@click.argument("name")
def add_domain(name):
    """Add a domain to arkOS LDAP"""
    try:
        client().roles.add_domain(name)
        logger.success('ctl:dom:add', 'Added {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))


@domain.command(name='delete')
@click.argument("name")
@click.option(
    "--yes", is_flag=True, callback=abort_if_false, expose_value=False,
    prompt='Are you sure you want to remove this domain?')
def delete_domain(name):
    """Delete an arkOS LDAP domain"""
    try:
        client().roles.delete_domain(name)
        logger.success('ctl:dom:delete', 'Deleted {0}'.format(name))
    except Exception as e:
        raise CLIException(str(e))
