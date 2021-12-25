import typer
import configparser

app = typer.Typer()

config = configparser.ConfigParser()

@app.command()
def validate(file_path: str):
	typer.echo(f"Reading config from: {file_path}")
	config.read(file_path)

if __name__ == "__main__":
	app()