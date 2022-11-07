FROM python:3.10-slim
# image is big
# image takes a long time to build
# image should also use a venv

# image runs as root

WORKDIR app

RUN groupadd --gid 50000 appgroup && useradd --uid 50000 --gid 50000 appuser

ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

USER 50000
