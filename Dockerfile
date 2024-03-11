ARG PYTHON_VERSION=3.10-slim-buster
ARG NODE_VERSION=18-bullseye

FROM node:$NODE_VERSION as node_modules
WORKDIR /opt
COPY package.json package-lock.json /opt/
RUN mkdir -p node_modules && npm install --ignore-scripts

FROM python:$PYTHON_VERSION

ARG ENVIRONMENT=production
ARG VERSION=latest

ENV PYTHONUNBUFFERED=1

ENV DB_HOSTNAME=db
ENV DB_USERNAME=mosp
ENV DB_PASSWORD=mosp

WORKDIR /app

COPY requirements.txt /app/

RUN pip install gunicorn[gevent]
RUN pip install -r requirements.txt

COPY mosp/ /app/mosp/
COPY contrib/ /app/contrib/
COPY instance/ /app/instance/
COPY migrations/ /app/migrations/
COPY --from=node_modules /opt/node_modules/ mosp/static/npm_components/

RUN pybabel compile -d mosp/translations

COPY app.py .
COPY entrypoint.sh .

ENV MOSP_VERSION=latest

ENV HOST=0.0.0.0
ENV PORT=5000
ENV MOSP_CONFIG=docker.py

VOLUME [ "/app/var" ]

EXPOSE 5000
CMD ./entrypoint.sh
