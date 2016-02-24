# -*- coding: utf-8 -*-
import click


@click.group()
def files():
    """File commands"""
    pass

@files.command()
@click.argument("path")
@click.pass_context
def edit(ctx, path):
    if ctx.obj["conn_method"] == "remote":
        data = ctx.obj["client"].files.get(path, content=True)
        out = click.edit(data["content"])
        if out:
            ctx.obj["client"].files.edit(path, out)
            click.secho("File saved as {}".format(path), bold=True)
        else:
            click.secho("File not saved.", bold=True)
    elif ctx.obj["conn_method"] == "local":
        with open(path, "r") as f:
            out = click.edit(f.read())
        if out:
            with open(path, "w") as f:
                f.write(out)
            click.secho("File saved as {}".format(path), bold=True)
        else:
            click.secho("File not saved.", bold=True)

GROUPS = [files]
