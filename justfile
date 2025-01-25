default: run

alias r := restore-env
alias d := dev-docker-compose
alias dr := deploy-railway

restore-env:
  [ -d '.venv' ] || uv sync --all-extras --all-groups

run:
  uv run cpn-telegram-bot

dev-docker-compose:
  docker compose up --watch --build

# Clean docker: stopped containers, networks not used by at least one container, dangling images, unused build cache
docker-clean:
  docker system prune

deploy-railway:
  railway up

clean:
  uvx cleanpy@0.5.1 .

precommit-run-all:
  uv run pre-commit run -a
