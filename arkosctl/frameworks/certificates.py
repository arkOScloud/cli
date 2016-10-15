# -*- coding: utf-8 -*-
"""Relates to commands for management of certificates."""
import click

from arkosctl import client, CLIException, logger
from arkosctl.utils import abort_if_false, handle_job


@click.group(name='cert')
def certificates():
    """SSL/TLS Certificates commands."""
    pass


@certificates.command(name='list')
def list_certs():
    """List all certificates."""
    try:
        certs = client().certificates.get()
        if not certs:
            logger.info('ctl:cert:list', 'No certificates found')
        llen = len(sorted(certs, key=lambda x: len(x["id"]))[-1]["id"])
        for x in sorted(certs, key=lambda x: x["id"]):
            klkt = "{0}-bit {1}".format(x["keylength"], x["keytype"])
            click.echo(
                click.style(
                    '{name: <{fill}}'.format(name=x["id"], fill=llen + 3),
                    fg="white", bold=True) +
                click.style(
                    '{name: <15}'.format(name=klkt),
                    fg="green") +
                click.style(x["domain"], fg="yellow")
            )
    except Exception as e:
        raise CLIException(str(e))


@certificates.command()
@click.argument("name")
def info(name):
    """Show information about a particular certificate."""
    try:
        cert = client().certificates.get(name)
        if not cert:
            logger.info('ctl:cert:info', 'No certificates found')
            return
        click.echo(click.style(cert["id"], fg="white", bold=True))
        click.echo(
            click.style(" * Domain: ", fg="yellow") + cert["domain"]
        )
        click.echo(
            click.style(" * Type: ", fg="yellow") +
            "{0}-bit {1}".format(cert["keylength"], cert["keytype"])
        )
        click.echo(
            click.style(" * SHA1: ", fg="yellow") + cert["sha1"]
        )
        click.echo(
            click.style(" * Expires: ", fg="yellow") +
            cert["expiry"].strftime("%c")
        )
        if cert.assigns:
            imsg = ", ".join([y["name"] for y in cert["assigns"]])
            click.echo(click.style(" * Assigned to: ", fg="yellow") + imsg)
    except Exception as e:
        raise CLIException(str(e))


@certificates.command(name='authorities')
def list_authorities():
    """List all certificate authorities (CAs)."""
    try:
        certs = client().certificates.get_authorities()
        if not certs:
            logger.info(
                'ctl:cert:authorities', 'No certificate authorities found'
            )
            return
        llen = len(sorted(certs, key=lambda x: len(x["id"]))[-1]["id"])
        for x in sorted(certs, key=lambda x: x["id"]):
            click.echo(
                click.style(
                    '{name: <{fill}}'.format(name=x["id"], fill=llen + 3),
                    fg="white", bold=True) + "Expires " +
                click.style(x["expiry"].strftime("%c"), fg="yellow")
            )
    except Exception as e:
        raise CLIException(str(e))


@certificates.command()
def assigns():
    """List all apps/sites that can use certificates."""
    click.echo("Apps/Sites that can use certificates:")
    try:
        assigns = client().certificates.get_possible_assigns()
        for x in assigns:
            imsg = click.style("(" + x["type"].capitalize() + ")", fg="green")
            click.echo(
                click.style(x["name"], fg="white", bold=True) + " " + imsg
            )
    except Exception as e:
        raise CLIException(str(e))


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
def generate(name, domain, country, state, locale, email,
             keytype, keylength):
    """Generate an SSL/TLS certificate."""
    if not domain:
        logger.error(
            "ctl:info:generate", "Choose a fully-qualified domain name of the "
            "certificate. Must match a domain present on the system"
        )
        domain = click.prompt("Domain name")
    if not country:
        logger.info(
            "ctl:cert:generate",
            "Two-character country code (ex.: 'US' or 'CA')"
        )
        country = click.prompt("Country code")
    if not state:
        state = click.prompt("State/Province")
    if not locale:
        locale = click.prompt("City/Town/Locale")
    if not email:
        email = click.prompt("Contact email [optional]")
    try:
        cmd = client().certificates.generate
        job, data = cmd(
            name, domain, country, state, locale, email, keytype, keylength)
        handle_job(job)
    except Exception as e:
        raise CLIException(str(e))


@certificates.command()
@click.option("--domain", help="Fully-qualified domain name of the cert."
              "Must match a domain present on the system")
def request(domain):
    """Request a free ACME certificate from Let's Encrypt."""
    if not domain:
        logger.error(
            "ctl:info:generate", "Choose a fully-qualified domain name of the "
            "certificate. Must match a domain present on the system"
        )
        domain = click.prompt("Domain name")
    try:
        client().certificates.request_acme_certificate(domain)
    except Exception as e:
        raise CLIException(str(e))


@certificates.command()
@click.argument("name")
@click.argument("certfile", type=click.File("r"))
@click.argument("keyfile", type=click.File("r"))
@click.option("--chainfile", default=None, type=click.File("r"),
              help="Optional file to include in cert chain")
def upload(name, certfile, keyfile, chainfile):
    """Upload an SSL/TLS certificate."""
    try:
        cmd = client().certificates.upload
        job, data = cmd(name, certfile, keyfile, chainfile)
        handle_job(job)
    except Exception as e:
        raise CLIException(str(e))


@certificates.command()
@click.argument("id")
@click.argument("type")
@click.argument("appid")
@click.argument("specialid", default=None)
def assign(id, type, appid, specialid):
    """Assign a certificate to an app or website."""
    try:
        client().certificates.assign(id, type, appid, specialid)
        logger.info(
            'ctl:cert:assign', 'Assigned {0} to {0}'.format(id, appid)
        )
    except Exception as e:
        raise CLIException(str(e))


@certificates.command()
@click.argument("id")
@click.argument("type")
@click.argument("appid")
@click.argument("specialid", default=None)
def unassign(id, type, appid, specialid):
    """Unassign a certificate from an app or website."""
    try:
        client().certificates.unassign(id, type, appid, specialid)
        logger.info(
            'ctl:cert:unassign', 'Unassigned {0} from {0}'.format(id, appid)
        )
    except Exception as e:
        raise CLIException(str(e))


@certificates.command()
@click.argument("id")
@click.option("--yes", is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to remove this site?')
def delete(id):
    """Delete a certificate."""
    try:
        client().certificates.delete(id=id)
        logger.success('ctl:cert:delete', 'Deleted {0}'.format(id))
    except Exception as e:
        raise CLIException(str(e))
