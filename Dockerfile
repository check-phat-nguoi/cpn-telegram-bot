FROM python:3.13.1-alpine

WORKDIR /app/

RUN apk add --no-cache \
  tesseract-ocr \
  tesseract-ocr-data-eng

COPY --chown=cpn:cpn pyproject.toml README.md /app/

RUN pip install --no-cache-dir --disable-pip-version-check .

COPY --chown=cpn:cpn src/ /app/

RUN pip install --no-cache-dir --disable-pip-version-check -e .

CMD [ "cpn-telegram-bot" ]
