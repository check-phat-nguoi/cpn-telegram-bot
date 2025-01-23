default: run

alias r := restore-env
alias d := deploy

restore-env:
  [ -d '.venv' ] || uv sync --all-extras --all-groups

run:
  uv run cpn-telegram-bot

deploy:
  railway up

clean:
  uvx cleanpy@0.5.1 .

precommit-run-all:
  uv run pre-commit run -a
