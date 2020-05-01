#---------
# Builder
#---------

# pull official base image
FROM python:3.8-alpine as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies: container
RUN apk update && apk add postgresql-dev gcc g++ python3-dev libffi-dev

# Upgrade pip: container
RUN pip install --upgrade pip

# install dependencies
COPY ./app/main/requirements /usr/src/requirements
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r /usr/src/requirements/prod.txt

# lint
RUN pip install flake8
COPY ./app .
#RUN flake8 --ignore=E501,F401 .


#---------
# Final
#---------

# pull official base image
FROM python:3.8-alpine

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create appropriate directories
ENV HOME=/home/app
ENV APP_HOME=$HOME/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add libpq libffi
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/requirements ./requirements
RUN pip install --upgrade --no-cache pip
RUN pip install --no-index --find-links=/wheels -r ./requirements/prod.txt

# copy entrypoint.sh
COPY ./docker/prod/entrypoint.sh $HOME/entrypoint.sh

# copy project
COPY ./app $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# Run entrypoint.sh: container
ENTRYPOINT ["/home/app/entrypoint.sh"]
