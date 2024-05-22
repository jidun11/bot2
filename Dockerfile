FROM ugorwx/fsub:alpine

WORKDIR /fsub

COPY pyproject.toml poetry.lock ./
RUN poetry install --quiet --no-interaction

COPY . .

CMD ["sh", "run.sh"]
