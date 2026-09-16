FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY DataBase ./DataBase
COPY static ./static
COPY templates ./templates
COPY schemas.py .
COPY security.py .
COPY conf_minio.py .
copy alembic ./alembic
copy alembic.ini .
copy tasks.py .
copy celery_app.py .
copy sender_email.py .
copy sender_html_on_email.py .

EXPOSE 8000

CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
