# Configuration System

FrameFlow uses a centralized configuration system so application code does not read environment variables or config files directly.

## Sources

Configuration may come from:

1. Built-in defaults
2. YAML configuration file
3. .env file
4. Environment variables

## Precedence

Environment variables override .env, which overrides the YAML configuration file, which overrides built-in defaults.

## Responsibilities

- Define typed settings models.
- Load configuration from supported sources.
- Apply defaults.
- Validate values at startup.
- Raise clear configuration errors.

## Initial Settings

- Application environment
- Host and port
- Data directory
- Database path
- Photo library path
- Log level

## Extension

Future display clients, including DAKboard, should add their own nested configuration sections without changing the core application settings.
