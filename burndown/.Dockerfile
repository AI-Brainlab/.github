FROM python:3.10.12-bookworm

LABEL org.opencontainers.image.source=https://github.com/AI-Brainlab/.github
LABEL org.opencontainers.image.description="Burndown fetcher"
LABEL org.opencontainers.image.licenses=MIT

ARG WORKDIR=/src/app
WORKDIR ${WORKDIR}

# https://vsupalov.com/docker-arg-env-variable-guide/
# https://bobcares.com/blog/debian_frontendnoninteractive-docker/
ARG DEBIAN_FRONTEND=noninteractive
# Timezone
ENV TZ="Asia/Bangkok"

RUN apt update && apt upgrade -y
# Set timezone
RUN apt install -y tzdata
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone

# Set locales
# https://leimao.github.io/blog/Docker-Locale/
RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL en_US.UTF-8 
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=${WORKDIR}

# pipenv
ENV PIPENV_VENV_IN_PROJECT=1
RUN pip install --upgrade pip
RUN pip install pipenv

RUN apt install -y gh

RUN --mount=type=bind,source=./app/Pipfile,target=Pipfile,readwrite \
    --mount=type=bind,source=./app/Pipfile.lock,target=Pipfile.lock,readwrite \
    # --mount=type=cache,target=/root/.pip \
    pipenv install --skip-lock

COPY ./app ${WORKDIR}

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

CMD pipenv run python3 main.py