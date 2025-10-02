FROM python:3.11-slim
WORKDIR /app
COPY ids_worker.py ./
RUN pip install redis
ENV REDIS_URL redis://redis:6379
CMD ["python","ids_worker.py"]