"""CLI entrypoint for RAG pipeline (Step 7에서 구현)."""

import typer

app = typer.Typer(help="RAG Pipeline CLI")


@app.command()
def hello() -> None:
    """Smoke test — 환경 설정이 정상인지 확인."""
    typer.echo("RAG pipeline is ready.")


if __name__ == "__main__":
    app()
