# -*- coding: utf-8 -*-
import click
import time

from functools import update_wrapper


class CLIException(click.ClickException):
    def show(self, file=None):
        # reimplement click.ClickException().show() to print bold and in red
        if self.message:
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


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        for x in self.list_commands(ctx):
            rv = click.Group.get_command(self, ctx, x)
            if hasattr(rv, "aliases") and cmd_name in rv.aliases:
                return rv


def handle_job(job):
    msg = None
    while job.status == "running":
        time.sleep(2)
        job.check()
        if job.message and job.message != msg:
            fg = None
            if job.message_class == "success":
                fg = "green"
            elif job.message_class == "warning":
                fg = "yellow"
            elif job.message_class == "error":
                fg = "red"
            click.echo((click.style(job.message_headline + " - ", fg=fg, bold=True) if job.message_headline != "None" else "") + click.style(job.message, fg=fg))
            msg = job.message
    if job.status != "success":
        if job.message and job.message != msg:
            raise Exception(job.message)
        elif not job.message or (job.message and job.message != msg):
            raise Exception("The process ended in error. Please check your server logs.")
        else:
            raise Exception()

def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

def str_fsize(sz):
    # Format a size int/float to the most appropriate string.
    if sz < 1024:
        return "%.1f bytes" % sz
    sz /= 1024.0
    if sz < 1024:
        return "%.1f Kb" % sz
    sz /= 1024.0
    if sz < 1024:
        return "%.1f Mb" % sz
    sz /= 1024.0
    return "%.1f Gb" % sz
