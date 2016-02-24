# -*- coding: utf-8 -*-
import click
import time


@click.group()
def certs():
    """SSL/TLS Certificates commands"""
    pass


@certs.command()
@click.pass_context
def list(ctx):
    """List all certificates"""
    if ctx.obj["conn_method"] == "remote":
        certs = ctx.obj["client"].certificates.get()
    elif ctx.obj["conn_method"] == "local":
        from arkos import certificates
        certs = [x.as_dict() for x in certificates.get()]
    if not certs:
        click.secho("No certificates found", bold=True)
    for x in sorted(certs, key=lambda x: x["id"]):
        click.echo(click.style(x["id"], fg="green") + click.style(" (" + x["domain"] +")", fg="yellow"))
        click.secho(u" ↳ Type: {}-bit {}".format(x["keylength"], x["keytype"]), fg="white")
        click.secho(u" ↳ SHA1: {}".format(x["sha1"]), fg="white")
        click.secho(u" ↳ Expires: {}".format(x["expiry"].strftime("%c")), fg="white")
        if x["assigns"]:
            click.secho(u" ↳ Assigned to: " + ", ".join([y["name"] for y in x["assigns"]]), fg="white")

@certs.command()
@click.pass_context
def authorities(ctx):
    """List all certificate authorities (CAs)"""
    if ctx.obj["conn_method"] == "remote":
        certs = ctx.obj["client"].certificates.get_authorities()
    elif ctx.obj["conn_method"] == "local":
        from arkos import certificates
        certs = [x.as_dict() for x in certificates.get_authorities()]
    if not certs:
        click.echo("No certificate authorities found")
    for x in sorted(certs, key=lambda x: x["id"]):
        click.secho(x["id"], fg="green")
        click.secho(u" ↳ Expires: {}".format(x["expiry"].strftime("%c")), fg="white")

@certs.command()
@click.pass_context
def assigns(ctx):
    """List all apps/sites that can use certificates"""
    click.echo("Apps/Sites that can use certificates:")
    if ctx.obj["conn_method"] == "remote":
        for x in ctx.obj["client"].certificates.get_possible_assigns():
            click.echo(click.style(x["name"], fg="green") + click.style(" (" + x["type"].capitalize() +")", fg="yellow"))

@certs.command()
@click.argument("name")
@click.option("--domain", required=True, help="Fully-qualified domain name of the certificate. Must match a domain present on the system")
@click.option("--country", required=True, help="Two-character country code (ex.: 'US' or 'CA')")
@click.option("--state", required=True, help="State or province")
@click.option("--locale", required=True, help="City/town name")
@click.option("--email", default="", help="Contact email")
@click.option("--keytype", default="RSA", help="SSL key type (ex.: 'RSA' or 'DSA')")
@click.option("--keylength", type=int, default=2048, help="SSL key length in bits")
@click.pass_context
def generate(ctx, name, domain, country, state, locale, email, keytype, keylength):
    """Generate an SSL/TLS certificate"""
    if ctx.obj["conn_method"] == "remote":
        job, data = ctx.obj["client"].certificates.generate(name, domain, country, state, locale,
            email, keytype, keylength)
        click.secho("Creating certificate {}, this may take a few minutes...".format(name), fg="green")
        while job.status == "running":
            time.sleep(2)
            job.check()
        if job.status != "success":
            click.ClickException("The process ended in error. Please check your logs.")
        click.secho("Certificate generated!", fg="yellow")

@certs.command()
@click.argument("name")
@click.argument("certfile", type=click.File("r"))
@click.argument("keyfile", type=click.File("r"))
@click.option("--chainfile", default=None, type=click.File("r"), help="Optional file to include in cert chain")
@click.pass_context
def upload(ctx, name, certfile, keyfile, chainfile):
    if ctx.obj["conn_method"] == "remote":
        click.secho("Uploading certificate {}...".format(name), fg="green")
        job, data = ctx.obj["client"].certificates.upload(name, certfile, keyfile, chainfile)
        while job.status == "running":
            time.sleep(2)
            job.check()
        if job.status != "success":
            click.ClickException("The process ended in error. Please check your logs.")
        click.secho("Certificate uploaded!", fg="yellow")

@certs.command()
@click.argument("id")
@click.argument("type")
@click.argument("appid")
@click.argument("specialid", default=None)
@click.pass_context
def assign(ctx, id, type, appid, specialid):
    """Assign a certificate to an app or website."""
    if ctx.obj["conn_method"] == "remote":
        ctx.obj["client"].certificates.assign(id, type, appid, specialid)
        click.echo("Certificate {} assigned to {}".format(id, appid))

@certs.command()
@click.argument("id")
@click.argument("type")
@click.argument("appid")
@click.argument("specialid", default=None)
@click.pass_context
def unassign(ctx, id, type, appid, specialid):
    """Unassign a certificate from an app or website."""
    if ctx.obj["conn_method"] == "remote":
        ctx.obj["client"].certificates.unassign(id, type, appid, specialid)
        click.echo("Certificate {} unassigned from {}".format(id, appid))

@certs.command()
@click.argument("id")
@click.pass_context
def delete(ctx, id):
    """Delete a certificate"""
    if ctx.obj["conn_method"] == "remote":
        ctx.obj["client"].certificates.delete(id=id)
        click.echo("Certificate deleted")


GROUPS = [certs]
