# SPDX-License-Identifier: Apache-2.0
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system frameflow && adduser --system --ingroup frameflow frameflow

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN python -m pip install --upgrade pip && python -m pip install .

USER frameflow
EXPOSE 8000

CMD ["python", "-c", "print('FrameFlow scaffold image built. Application entrypoint will be added in Milestone 1.')"]
