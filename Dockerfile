FROM python:3.6
COPY . /code/loadlamb
WORKDIR code/loadlamb
RUN pip install poetry & poetry install
WORKDIR /code/loadlamb