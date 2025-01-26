FROM python:3.13.1-alpine

WORKDIR /app/

RUN apk add --no-cache \
  tesseract-ocr \
  tesseract-ocr-data-eng

RUN touch /app/README.md
COPY --chown=cpn:cpn telegram-bot/pyproject.toml /app/

RUN pip install --no-cache-dir --disable-pip-version-check .

COPY --chown=cpn:cpn core/ /app/core/
RUN pip install --no-cache-dir --disable-pip-version-check --upgrade --no-dependencies --editable ./core

COPY --chown=cpn:cpn telegram-bot/src/ /app/src/
RUN pip install --no-cache-dir --disable-pip-version-check --editable .

CMD [ "cpn-telegram-bot" ]
