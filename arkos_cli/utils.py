# -*- coding: utf-8 -*-
import click


class CLIException(click.ClickException):
    def show(self, file=None):
        # reimplement click.ClickException().show() to print bold and in red
        click.secho("Error: {}".format(self.format_message()), fg="red",
            bold=True, err=True)


class ClickMessager:
    def __init__(self, cls="", msg="", head=""):
        if cls == "error" and msg:
            raise click.ClickException(msg)
        if head:
            click.secho(head, fg="green")
        click.secho(msg, bold=True)

    def update(self, cls, msg, head=""):
        if cls == "error":
            raise click.ClickException(msg)
        click.secho(u" ↳ {}".format(msg), fg="yellow")

    def complete(self, cls, msg, head=""):
        if cls == "error":
            raise click.ClickException(msg)
        click.secho(msg, bold=True)
