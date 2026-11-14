FROM node:22.13.1-alpine3.21 AS frontend-build
RUN apk add --no-cache git
WORKDIR /frontend
COPY frontend/ ./
# Railway's source snapshot does not include git submodules, so frontend/ arrives
# empty. Fall back to cloning the public frontend repo at the pinned commit.
# Keep FRONTEND_REF in sync with the frontend submodule pointer.
ARG FRONTEND_REPO=https://github.com/ivanbright/rodai-frontend.git
ARG FRONTEND_REF=ef0419b10d33c56f9fb2103bac56f17d4b70ac49
RUN if [ ! -f package.json ]; then \
      git init -q . && git remote add origin "$FRONTEND_REPO" \
      && git fetch -q --depth 1 origin "$FRONTEND_REF" && git checkout -q FETCH_HEAD \
      && rm -rf .git; \
    fi
RUN npm ci
RUN npm run build

FROM python:3.12.8-slim-bookworm AS build
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
COPY backend/pyproject.toml backend/requirements.lock ./
RUN python -m pip install --no-cache-dir --upgrade pip==25.0.1 \
    && python -m pip install --no-cache-dir --prefix=/install -r requirements.lock \
    && python -m pip install --no-cache-dir --prefix=/install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
COPY backend/requirements.inference.lock ./requirements.inference.lock
RUN python -m pip install --no-cache-dir --prefix=/install -r requirements.inference.lock
COPY backend/rodai ./rodai
COPY backend/migrations ./migrations
COPY backend/alembic.ini ./alembic.ini

FROM python:3.12.8-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/usr/local/bin:${PATH}"
WORKDIR /app
RUN groupadd --system rodai && useradd --system --gid rodai --home-dir /app rodai \
    && mkdir -p /var/lib/rodai \
    && chown -R rodai:rodai /app /var/lib/rodai
COPY --from=build /install /usr/local
COPY --from=build --chown=rodai:rodai /build/rodai /app/rodai
COPY --from=build --chown=rodai:rodai /build/migrations /app/migrations
COPY --from=build --chown=rodai:rodai /build/alembic.ini /app/alembic.ini
COPY --from=frontend-build --chown=rodai:rodai /frontend/dist /app/frontend/dist
USER rodai
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD sh -c 'python -c "import os,urllib.request; urllib.request.urlopen(\"http://127.0.0.1:{}/api/v1/health\".format(os.getenv(\"PORT\",\"8000\")), timeout=4)"' || exit 1
CMD ["sh", "-c", "uvicorn rodai.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
