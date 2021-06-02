# https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
FROM python:3.8 as builder
# set working directory
WORKDIR /code

# copy dependencies
COPY requirements.txt /code/

# # install dependencies
RUN pip install -r requirements.txt

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

# set environment variables
ENV PYTHONWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# set working directory
WORKDIR /code

COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
# copy dependencies
COPY requirements.txt /code/

# install dependencies
# RUN pip install -r requirements.txt

# copy project
COPY . /code/

# expose port
EXPOSE 5000
