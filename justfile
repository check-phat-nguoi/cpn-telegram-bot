default: run

alias r := restore-env

restore-env:
  [ -d '.venv' ] || uv sync --all-extras --all-groups

run:
  uv run cpn-tele-bot

clean:
  uvx cleanpy@0.5.1 .

precommit-run-all:
  uv run pre-commit run -a
