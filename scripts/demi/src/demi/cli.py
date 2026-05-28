import typer
from demi.plugin_stats.commands import plugin_stats_app

app = typer.Typer(help="demi — Claude Code 개발환경 관리 도구")
app.add_typer(plugin_stats_app, name="plugin-stats")

if __name__ == "__main__":
    app()
