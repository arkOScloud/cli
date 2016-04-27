# -*- coding: utf-8 -*-
import click

from arkos_cli.utils import u, AliasedGroup, abort_if_false, CLIException


@click.command(cls=AliasedGroup)
def roles():
    """User/group/domain commands"""
    pass

@roles.command()
@click.pass_context
def users(ctx):
    """List users"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].roles.get_users()
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import users
            data = [x.serialized for x in users.get()]
    except Exception as e:
        raise CLIException(str(e))
    else:
        for x in data:
            click.echo(click.style(x["name"], fg="green") + click.style(" ({0})".format(x["id"]), fg="yellow"))
            click.secho(u(" ↳ Name: {0}").format(x["first_name"] + (" " + x["last_name"] if x["last_name"] else "")), fg="white")
            click.secho(u(" ↳ Mail Addresses: {0}").format(", ".join(x["mail_addresses"])), fg="white")
            click.secho(u(" ↳ Types: {0}").format(", ".join([y for y in ["sudo" if x["sudo"] else None, "admin" if x["admin"] else None] if y])), fg="white")

@roles.command()
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True,
              confirmation_prompt=True, help="Password for new user")
@click.option("--domain", prompt=True, help="Domain name to assign the new user to")
@click.option("--first-name", prompt="First name or pseudonym", help="First name or pseudonym")
@click.option("--last-name", prompt="Last name (optional)", help="Last name (optional)")
@click.option("--admin", is_flag=True, prompt="Give the user admin privileges?", help="Give the user admin privileges?")
@click.option("--sudo", is_flag=True, prompt="Give the user command-line sudo privileges?", help="Give the user command-line sudo privileges?")
@click.pass_context
def useradd(ctx, name, password, domain, first_name, last_name, admin, sudo):
    """Add a user to arkOS LDAP"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].roles.add_user(name, password, domain, first_name,
                last_name, admin, sudo)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import users
            u = users.User(name=name, first_name=first_name, last_name=last_name,
                domain=domain, admin=admin, sudo=sudo)
            u.add(password)
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("User added successfully", fg="green")

@roles.command()
@click.argument("name")
@click.option("--domain", default=None, help="Domain name to assign the new user to")
@click.option("--first-name", default=None, help="First name or pseudonym")
@click.option("--last-name", default=None, help="Last name (optional)")
@click.option("--admin", is_flag=True, default=None, help="Give the user admin privileges?")
@click.option("--sudo", is_flag=True, default=None, help="Give the user command-line sudo privileges?")
@click.pass_context
def usermod(ctx, name, domain, first_name, last_name, admin, sudo):
    """Edit an arkOS LDAP user"""
    try:
        if ctx.obj["conn_method"] == "remote":
            users = ctx.obj["client"].roles.get_users()
            uid = [y["id"] for y in users if y["name"] == name]
            if not uid:
                raise CLIException("No such user")
            uid = uid[0]
            ctx.obj["client"].roles.edit_user(uid, domain, first_name,
                last_name, "", admin, sudo)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import users
            u = users.get(name=name)
            u.domain = domain or u.domain
            u.first_name = first_name or u.first_name
            u.last_name = last_name if last_name != None else u.last_name
            u.admin = admin if admin != None else u.admin
            u.sudo = sudo if sudo != None else u.sudo
            u.update()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("User edited successfully", fg="green")

@roles.command()
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True,
              confirmation_prompt=True, help="Password for new user")
@click.pass_context
def chpasswd(ctx, name, password):
    """Change an arkOS LDAP user password"""
    try:
        if ctx.obj["conn_method"] == "remote":
            users = ctx.obj["client"].roles.get_users()
            uid = [y["id"] for y in users if y["name"] == name]
            if not uid:
                raise CLIException("No such user")
            uid = uid[0]
            ctx.obj["client"].roles.edit_user(uid, passwd=password)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import users
            u = users.get(name=name)
            u.update(password)
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Password changed successfully", fg="green")

@roles.command()
@click.argument("name")
@click.option("--yes", is_flag=True, callback=abort_if_false,
              expose_value=False, prompt='Are you sure you want to remove this user?')
@click.pass_context
def userdel(ctx, name):
    """Delete an arkOS LDAP user"""
    try:
        if ctx.obj["conn_method"] == "remote":
            users = ctx.obj["client"].roles.get_users()
            uid = [y["id"] for y in users if y["name"] == name]
            if not uid:
                raise CLIException("No such user")
            uid = uid[0]
            ctx.obj["client"].roles.delete_user(uid)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import users
            u = users.get(name=name)
            u.delete()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("User deleted", fg="red")

@roles.command()
@click.pass_context
def groups(ctx):
    """List groups"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].roles.get_groups()
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import groups
            data = [x.serialized for x in groups.get()]
    except Exception as e:
        raise CLIException(str(e))
    else:
        for x in data:
            click.echo(click.style(x["name"], fg="green") + click.style(" ({})".format(x["id"]), fg="yellow"))
            click.secho(u(" ↳ Members: {0}").format(", ".join(x["users"])), fg="white")

@roles.command()
@click.argument("name")
@click.option("--users", multiple=True)
@click.pass_context
def groupadd(ctx, name, users):
    """Add a group to arkOS LDAP"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].roles.add_group(name, users)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import groups
            g = groups.Group(name=name, users=users)
            g.add()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Group added successfully", fg="green")

@roles.command()
@click.argument("name")
@click.argument("operation", type=click.Choice(["add", "remove"]))
@click.argument("username")
@click.pass_context
def groupmod(ctx, name, operation, username):
    """Add/remove users from an arkOS LDAP group"""
    try:
        if ctx.obj["conn_method"] == "remote":
            groups = ctx.obj["client"].roles.get_groups()
            gid = [y for y in groups if y["name"] == name]
            if not gid:
                raise CLIException("No such group")
            gid, members = gid[0]["id"], gid[0]["members"]
            if operation == "add":
                members.append(username)
            else:
                members.remove(username)
            ctx.obj["client"].roles.edit_group(gid, members)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import groups
            g = groups.get(name=name)
            if operation == "add":
                g.users.append(username)
            else:
                g.users.remove(username)
            g.update()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Group edited successfully", fg="green")

@roles.command()
@click.argument("name")
@click.option("--yes", is_flag=True, callback=abort_if_false,
              expose_value=False, prompt='Are you sure you want to remove this group?')
@click.pass_context
def groupdel(ctx, name):
    """Delete an arkOS LDAP group"""
    try:
        if ctx.obj["conn_method"] == "remote":
            groups = ctx.obj["client"].roles.get_groups()
            gid = [y["id"] for y in groups if y["name"] == name]
            if not gid:
                raise CLIException("No such group")
            gid = gid[0]
            ctx.obj["client"].roles.delete_group(gid)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import groups
            g = groups.get(name=name)
            g.delete()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Group deleted", fg="red")

@roles.command()
@click.pass_context
def domains(ctx):
    """List domains"""
    try:
        if ctx.obj["conn_method"] == "remote":
            data = ctx.obj["client"].roles.get_domains()
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import domains
            data = [x.serialized for x in domains.get()]
    except Exception as e:
        raise CLIException(str(e))
    else:
        for x in data:
            click.echo(x["id"])

@roles.command()
@click.argument("name")
@click.pass_context
def domainadd(ctx, name):
    """Add a domain to arkOS LDAP"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].roles.add_domain(name)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import domains
            d = domains.Domain(name=name)
            d.add()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Domain added successfully", fg="green")

@roles.command()
@click.argument("name")
@click.option("--yes", is_flag=True, callback=abort_if_false,
              expose_value=False, prompt='Are you sure you want to remove this domain?')
@click.pass_context
def domaindel(ctx, name):
    """Delete an arkOS LDAP domain"""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].roles.delete_domain(name)
        elif ctx.obj["conn_method"] == "local":
            from arkos.system import domains
            d = domains.get(name)
            d.remove()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Domain deleted", fg="red")


users.aliases = ["list", "list-users"]
groups.aliases = ["list-groups"]
useradd.aliases = ["add-user", "create-user", "adduser"]
groupadd.aliases = ["add-group", "create-group", "addgroup"]
domainadd.aliases = ["add-domain", "create-domain", "adddomain"]
usermod.aliases = ["edit-user", "edituser"]
groupmod.aliases = ["edit-group", "editgroup", "add-members", "remove-members"]
chpasswd.aliases = ["passwd", "password", "change-password"]
userdel.aliases = ["delete-user", "del-user", "remove-user"]
groupdel.aliases = ["delete-group", "del-group", "remove-group"]
domaindel.aliases = ["delete-domain", "del-domain", "remove-domain"]
GROUPS = [[roles, "users", "user", "usr", "groups", "group", "grp", "domains", "domain", "dom"]]
