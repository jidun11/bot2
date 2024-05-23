FROM ugorwx/fsub:alpine

WORKDIR /fsub

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create true
RUN poetry install --no-interaction --no-ansi

COPY . .

CMD ["sh", "run.sh"]
