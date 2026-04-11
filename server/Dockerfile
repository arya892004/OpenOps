FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir \
    openenv-core \
    fastapi \
    uvicorn[standard] \
    pydantic \
    openai

ENV PYTHONPATH="/app:"

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]