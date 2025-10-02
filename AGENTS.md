# Repository Guidelines

## Project Structure & Module Organization
- `synthetic_data_kit/` holds the CLI (`cli.py`) and modular packages: `core/`, `generators/`, `models/`, `parsers/`, `server/`, and `utils/`.
- `configs/config.yaml` provides default runtime settings; override values per environment rather than editing in place.
- `data/` is ignored by git; use staged subfolders (`input`, `parsed`, `generated`, `curated`, `final`) when running pipelines.
- `tests/` mirrors runtime modules with `unit/`, `integration/`, and `functional/` suites plus shared fixtures in `tests/conftest.py`.
- `use-cases/` documents end-to-end examples; keep additions self-contained with README updates.

## Build, Test, and Development Commands
- `python -m venv .venv && .\.venv\Scripts\Activate` creates a local environment.
- `pip install -e .[dev]` installs the CLI with dev tooling.
- `synthetic-data-kit --help` lists CLI stages; use `synthetic-data-kit ingest data/input/report.pdf` as a template.
- `pytest` runs the default test suite; add markers such as `pytest -m "unit"` for targeted runs.
- `pytest --cov=synthetic_data_kit --cov-report=term-missing` verifies coverage before merging.
- `pre-commit run --all-files` enforces formatting and static checks.

## Coding Style & Naming Conventions
- Follow Ruff formatting defaults (`line-length = 100`, spaces only, double quotes); run `ruff format synthetic_data_kit tests` before committing.
- Prefer descriptive snake_case for modules, functions, and variables; constants in UPPER_CASE.
- Type hints are mandatory; mypy strict mode blocks untyped defs. Execute `mypy synthetic_data_kit tests` locally.

## Testing Guidelines
- Mirror file names with `test_<module>.py`; functions begin with `test_`.
- Scope fixtures via `tests/conftest.py` when they are shared, otherwise keep them local to minimize coupling.
- Use pytest markers (`@pytest.mark.unit`/`integration`/`functional`) so CI can slice runs.
- When extending the CLI, add regression coverage that exercises both CLI entry points and the underlying service layer.

## Commit & Pull Request Guidelines
- Commit messages follow a short imperative summary (`fixing unit tests for additional parsers`); keep body optional but clarify rationale for non-trivial changes.
- Squash fixups before opening a PR. Reference GitHub issues with `Closes #123` when applicable.
- PRs must include: clear description of problem/solution, testing evidence (`pytest`/coverage output), configuration changes, and screenshots for UI updates.
- Request review from code owners of affected areas (e.g., CLI vs. server) and ensure docs in `DOCS.md` or `use-cases/` stay in sync.
