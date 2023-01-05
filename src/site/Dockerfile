FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /app
WORKDIR /app

RUN pip install requests django Pillow psycopg2 coveralls python-dotenv

RUN chown -R $USER:$USER manage.py

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]