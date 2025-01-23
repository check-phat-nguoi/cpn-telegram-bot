FROM python:3.13.1-alpine

WORKDIR /app/

RUN apk add --no-cache \
  tesseract-ocr \
  tesseract-ocr-data-eng

COPY . /app/

RUN pip install -e .

CMD [ "cpn-telegram-bot" ]
