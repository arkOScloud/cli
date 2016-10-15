# -*- coding: utf-8 -*-
"""Utility commands."""
import click
import time


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
            raise CLIException(job.message)
        elif not job.message or (job.message and job.message != msg):
            raise CLIException(
                "The process ended in error. Please check your server logs.")
        else:
            raise CLIException("Unknown error")


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
