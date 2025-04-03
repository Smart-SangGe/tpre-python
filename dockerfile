FROM python:3.13-slim AS base
WORKDIR /app
COPY ./pyproject.toml /app/
COPY lib/* /usr/local/lib/
RUN ldconfig && \
  pip install -i https://git.mamahaha.work/api/packages/sangge/pypi/simple/ ecc-rs==0.1.2 --no-cache-dir

# Development stage
FROM base AS dev
RUN pip install -e ".[dev]" -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir

# Test stage
FROM base AS test
COPY ./tests /app/tests
RUN pip install -e ".[test]" -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir
ENTRYPOINT ["pytest", "/app/tests"]
CMD ["-xvs"]

# Deployment stage
FROM base AS deploy
WORKDIR /app
COPY --from=base /usr/local/lib/* /usr/local/lib/
COPY src /app
RUN ldconfig
