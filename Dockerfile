ARG IMAGE_REGISTRY=""
FROM ${IMAGE_REGISTRY}python:3.11-slim-bullseye
# FROM python:3.11-slim-bullseye

COPY ./certs/nexus.petrobras.com.br.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

RUN echo 'deb [trusted=yes] https://nexus.petrobras.com.br/nexus/repository/apt-debian-deb-bullseye/ bullseye main' > /etc/apt/sources.list && \
    apt update && \
    apt install -y gcc libpq5 && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip config set global.index https://nexus.petrobras.com.br/nexus/repository/pypi-all/pypi && \
    pip config set global.index-url https://nexus.petrobras.com.br/nexus/repository/pypi-all/simple && \
    pip config set global.trusted-host "pypi.org pypi.python.org files.pythonhosted.org nexus.petrobras.com.br"

WORKDIR /user/app

COPY requirements.txt .
COPY confiacim_api/ confiacim_api/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "confiacim_api.app:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
