# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.9.13 as build

# Create app directory
WORKDIR /base

# setup env vars for container
ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=5001
ENV ENV='production'

# Move required items into working directory
COPY /client/dist /base/client/dist
COPY /server/ /base/server
COPY requirements.txt /base/requirements.txt
COPY prod_run.sh /base/prod_run.sh

# Instal python dependencies
RUN pip install -r requirements.txt
RUN chmod a+x prod_run.sh

# Expose port and start server
EXPOSE 5001

CMD ["./prod_run.sh"]
