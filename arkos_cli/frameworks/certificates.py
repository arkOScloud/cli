# -*- coding: utf-8 -*-
"""Relates to commands for management of certificates."""
import click

from arkos_cli.utils import u, AliasedGroup, abort_if_false, handle_job
from arkos_cli.utils import CLIException, ClickMessager


@click.command(cls=AliasedGroup)
def certificates():
    """SSL/TLS Certificates commands."""
    pass


@certificates.command()
@click.pass_context
def list(ctx):
    """List all certificates."""
    try:
        if ctx.obj["conn_method"] == "remote":
            certs = ctx.obj["client"].certificates.get()
        elif ctx.obj["conn_method"] == "local":
            from arkos import certificates
            certs = [x.as_dict for x in certificates.get()]
    except Exception as e:
        raise CLIException(str(e))
    else:
        if not certs:
            click.secho("No certificates found", bold=True)
        for x in sorted(certs, key=lambda x: x["id"]):
            imsg = click.style(" (" + x["domain"] + ")", fg="yellow")
            click.echo(click.style(x["id"], fg="green") + imsg)
            tmsg = u(" ↳ Type: {0}-bit {1}")
            click.secho(tmsg.format(x["keylength"], x["keytype"]), fg="white")
            click.secho(u(" ↳ SHA1: {0}").format(x["sha1"]), fg="white")
            etime = x["expiry"].strftime("%c")
            click.secho(u(" ↳ Expires: {0}").format(etime), fg="white")
            if x["assigns"]:
                imsg = ", ".join([y["name"] for y in x["assigns"]])
                click.secho(u(" ↳ Assigned to: ") + imsg, fg="white")


@certificates.command()
@click.pass_context
def list_authorities(ctx):
    """List all certificate authorities (CAs)."""
    try:
        if ctx.obj["conn_method"] == "remote":
            certs = ctx.obj["client"].certificates.get_authorities()
        elif ctx.obj["conn_method"] == "local":
            from arkos import certificates
            certs = [x.as_dict for x in certificates.get_authorities()]
    except Exception as e:
        raise CLIException(str(e))
    else:
        if not certs:
            click.echo("No certificate authorities found")
        for x in sorted(certs, key=lambda x: x["id"]):
            click.secho(x["id"], fg="green")
            click.secho(u(" ↳ Expires: {}").format(x["expiry"].strftime("%c")),
                        fg="white")


@certificates.command()
@click.pass_context
def assigns(ctx):
    """List all apps/sites that can use certificates."""
    click.echo("Apps/Sites that can use certificates:")
    try:
        if ctx.obj["conn_method"] == "remote":
            assigns = ctx.obj["client"].certificates.get_possible_assigns()
        elif ctx.obj["conn_method"] == "local":
            from arkos import applications, websites
            assigns = []
            assigns.append({"type": "genesis", "id": "genesis",
                            "name": "arkOS Genesis/API"})
            for x in websites.get():
                assigns.append({"type": "website", "id": x.id,
                                "name": x.id if x.meta else x.name})
            for x in applications.get(installed=True):
                if x.type == "app" and x.uses_ssl:
                    for y in x.get_ssl_able():
                        assigns.append(y)
    except Exception as e:
        raise CLIException(str(e))
    else:
        for x in assigns:
            imsg = click.style("(" + x["type"].capitalize() + ")", fg="yellow")
            click.echo(click.style(x["name"], fg="green") + " " + imsg)


@certificates.command()
@click.argument("name")
@click.option("--domain", help="Fully-qualified domain name of the cert."
              "Must match a domain present on the system")
@click.option("--country", help="Two-character country code (ex.: 'US', 'CA')")
@click.option("--state", help="State or province")
@click.option("--locale", help="City/town name")
@click.option("--email", default="", help="Contact email")
@click.option("--keytype", default="RSA",
              help="SSL key type (ex.: 'RSA' or 'DSA')")
@click.option("--keylength", type=int, default=2048,
              help="SSL key length in bits")
@click.pass_context
def generate(ctx, name, domain, country, state, locale, email,
             keytype, keylength):
    """Generate an SSL/TLS certificate."""
    if not domain:
        click.echo("Choose a fully-qualified domain name of the certificate. "
                   "Must match a domain present on the system")
        domain = click.prompt("Domain name")
    if not country:
        click.echo("Two-character country code (ex.: 'US' or 'CA')")
        country = click.prompt("Country code")
    if not state:
        state = click.prompt("State/Province")
    if not locale:
        locale = click.prompt("City/Town/Locale")
    if not email:
        email = click.prompt("Contact email [optional]")
    try:
        if ctx.obj["conn_method"] == "remote":
            cmd = ctx.obj["client"].certificates.generate
            job, data = cmd(name, domain, country, state, locale,
                            email, keytype, keylength)
            smsg = "Creating certificate {0}, this may take a few minutes..."
            click.secho(smsg.format(name), fg="green")
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            from arkos import certificates
            cmd = certificates.generate_certificate
            cmd(name, domain, country, state, locale, email, keytype,
                keylength, ClickMessager())
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Certificate generated", fg="yellow")


@certificates.command()
@click.argument("name")
@click.argument("certfile", type=click.File("r"))
@click.argument("keyfile", type=click.File("r"))
@click.option("--chainfile", default=None, type=click.File("r"),
              help="Optional file to include in cert chain")
@click.pass_context
def upload(ctx, name, certfile, keyfile, chainfile):
    """Upload an SSL/TLS certificate."""
    try:
        if ctx.obj["conn_method"] == "remote":
            click.secho("Uploading certificate {}...".format(name), fg="green")
            cmd = ctx.obj["client"].certificates.upload
            job, data = cmd(name, certfile, keyfile, chainfile)
            handle_job(job)
        elif ctx.obj["conn_method"] == "local":
            from arkos import certificates
            cmd = certificates.upload_certificate
            cmd(name, certfile.read(), keyfile.read(),
                chainfile.read() if chainfile else None, ClickMessager())
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.secho("Certificate uploaded!", fg="yellow")


@certificates.command()
@click.argument("id")
@click.argument("type")
@click.argument("appid")
@click.argument("specialid", default=None)
@click.pass_context
def assign(ctx, id, type, appid, specialid):
    """Assign a certificate to an app or website."""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].certificates.assign(id, type, appid, specialid)
            click.echo("Certificate {} assigned to {}".format(id, appid))
        elif ctx.obj["conn_method"] == "local":
            from arkos import certificates
            cert = certificates.get(id)
            cert.assign({"type": type, "id": appid, "aid": appid,
                         "sid": specialid})
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.echo("Certificate {} assigned to {}".format(id, appid))


@certificates.command()
@click.argument("id")
@click.argument("type")
@click.argument("appid")
@click.argument("specialid", default=None)
@click.pass_context
def unassign(ctx, id, type, appid, specialid):
    """Unassign a certificate from an app or website."""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].certificates.unassign(id, type, appid, specialid)
        elif ctx.obj["conn_method"] == "local":
            from arkos import certificates
            cert = certificates.get(id)
            cert.unassign({"type": type, "id": appid, "aid": appid,
                           "sid": specialid})
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.echo("Certificate {} unassigned from {}".format(id, appid))


@certificates.command()
@click.argument("id")
@click.option("--yes", is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to remove this site?')
@click.pass_context
def delete(ctx, id):
    """Delete a certificate."""
    try:
        if ctx.obj["conn_method"] == "remote":
            ctx.obj["client"].certificates.delete(id=id)
        elif ctx.obj["conn_method"] == "local":
            from arkos import certificates
            cert = certificates.get(id)
            cert.remove()
    except Exception as e:
        raise CLIException(str(e))
    else:
        click.echo("Certificate deleted")


assigns.aliases = ["types", "apps", "sites"]
generate.aliases = ["create", "add"]
list_authorities.aliases = ["list-authorities", "authorities", "cas", "auths"]
delete.aliases = ["remove"]
GROUPS = [[certificates, "certificate", "crt", "cert", "certs"]]
