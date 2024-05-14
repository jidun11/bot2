FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1

RUN apk update \
    && apk add --no-cache \
        bash \
        build-base \
        curl \
        git

RUN pip install --upgrade pip --no-warn-script-location

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false \
    && poetry install \
        --only main \
        --no-interaction \
        --no-ansi --no-root

RUN mkdir /fsub

COPY . /fsub/

WORKDIR /fsub

CMD ["python", "main.py"]
