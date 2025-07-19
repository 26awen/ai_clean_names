import click
from ai_clean_names.libs import batch_rename
from rich import print


@click.command()
@click.argument("filepath")
def cli(filepath: str):
    try:
        batch_rename(filepath)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    cli()
