# -*- coding: utf-8 -*-
"""Utility commands."""
import click
import sys
import time


class CLIException(click.ClickException):
    """Reimplement click.ClickException() to print bold & in red."""

    def show(self, file=None):
        """Reimplement."""
        if self.message:
            click.secho("Error: {}".format(self.format_message()), fg="red",
                        bold=True, err=True)


class ClickMessager:
    """Message handler for remote synchronous processes."""

    def __init__(self, cls="", msg="", head=""):
        """Initialize."""
        if cls == "error" and msg:
            raise CLIException(msg)
        hd = click.style(head + " - ", fg=self._get_cls(cls), bold=True)
        click.echo((hd if head else "") + click.style(msg, fg=self._getcls(cls)))

    def _getcls(self, mcls):
        if mcls == "success":
            return "green"
        elif mcls == "warning":
            return "yellow"
        elif mcls == "error":
            return "red"
        elif mcls == "info":
            return "cyan"
        else:
            return None

    def update(self, cls, msg, head=""):
        """Update message."""
        if cls == "error":
            raise CLIException(msg)
        hd = click.style(head + " - ", fg=self._getcls(cls), bold=True)
        click.echo((hd if head else "") + click.style(msg, fg=self._get_cls(cls)))

    def complete(self, cls, msg, head=""):
        """Complete message."""
        if cls == "error":
            raise CLIException(msg)
        hd = click.style(head + " - ", fg=self._get_cls(cls), bold=True)
        click.echo((hd if head else "") + click.style(msg, fg=self._get_cls(cls)))


class AliasedGroup(click.Group):
    """Group to handle aliased commands."""

    def get_command(self, ctx, cmd_name):
        """Get command with all aliases."""
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        for x in self.list_commands(ctx):
            rv = click.Group.get_command(self, ctx, x)
            if hasattr(rv, "aliases") and cmd_name in rv.aliases:
                return rv


def handle_job(job):
    """Check job result endpoints and display messages accordingly."""
    msg = None
    while job.status == "running":
        time.sleep(2)
        job.check()
        if job.message and job.message != msg:
            fg = None
            if job.message["level"] == "success":
                fg = "green"
            elif job.message["level"] == "warning":
                fg = "yellow"
            elif job.message["level"] == "error":
                fg = "red"
            hd = click.style(job.message["title"] + " - ", fg=fg, bold=True)
            hd = (hd if job.message["title"] != "None" else "")
            click.echo(hd + click.style(job.message["message"], fg=fg))
            msg = job.message
    if job.status != "success":
        if job.message and job.message != msg:
            raise Exception(job.message)
        elif not job.message or (job.message and job.message != msg):
            raise Exception("The process ended in error. "
                            "Please check your server logs.")
        else:
            raise Exception()


def abort_if_false(ctx, param, value):
    """Abort the command if the value resolves to be false."""
    if not value:
        ctx.abort()


def str_fsize(sz):
    """Format a size int/float to the most appropriate string."""
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


def u(x):
    """Handle code with UTF-8 symbols cross-version."""
    if sys.version_info < (3,):
        import codecs
        return codecs.unicode_escape_decode(x)[0]
    else:
        return x
