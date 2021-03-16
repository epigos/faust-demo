FROM python:3.8-buster

RUN mkdir /code
WORKDIR /code

# install poetry package manager
RUN pip install -U pip
RUN pip install poetry
# install project dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

COPY workers/ /code
