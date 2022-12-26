FROM python:3.10

COPY . /app
WORKDIR /app

RUN pip install requests django Pillow psycopg2

EXPOSE 8000

CMD ["python", "manage.py", "runserver"]