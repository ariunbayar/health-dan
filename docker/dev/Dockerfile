# pull official base image
FROM python:3.8-alpine

# Set work directory: container
WORKDIR /usr/src/app

# Set environment variables: container
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies: container
RUN apk update && apk add postgresql-dev g++ python3-dev

# Upgrade pip: container
RUN pip install --upgrade pip

# Copy requirements
COPY ./app/main/requirements /usr/src/app/main/requirements

# Install requirements
RUN pip install -r /usr/src/app/main/requirements/dev.txt

# Copy entrypoint.sh
COPY ./docker/dev/entrypoint.sh /usr/src/entrypoint.sh

# Copy project files
COPY ./app /usr/src/app/

# Run entrypoint.sh
ENTRYPOINT ["/usr/src/entrypoint.sh"]
