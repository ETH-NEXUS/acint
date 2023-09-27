FROM python:3.11-slim

# Optimise python and debian in docker
ENV PYTHONUNBUFFERED 1
ENV PIP_BREAK_SYSTEM_PACKAGES 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV DEBIAN_FRONTEND noninteractive

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./app /app
WORKDIR /app

CMD [ "./acint.py" ]


