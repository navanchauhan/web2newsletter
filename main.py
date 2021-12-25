import typer

from web2newsletter import config, newsletter

app = typer.Typer()

app.add_typer(config.app, name="config")
app.add_typer(newsletter.app, name="newsletter")

if __name__ == "__main__":
	app()