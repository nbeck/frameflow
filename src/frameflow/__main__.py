"""Application entry point: python -m frameflow / uv run frameflow."""

import uvicorn

from frameflow.config import load_settings


def main() -> None:
    settings = load_settings()
    uvicorn.run("frameflow.api.app:app", host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
