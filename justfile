default: run

alias r := restore-env
alias d := deploy-docker-compose
alias dr := deploy-railway

restore-env:
  [ -d '.venv' ] || uv sync --all-extras --all-groups

run:
  uv run cpn-telegram-bot

deploy-docker-compose:
  docker-compose up --watch --build

deploy-railway:
  railway up

clean:
  uvx cleanpy@0.5.1 .

precommit-run-all:
  uv run pre-commit run -a
