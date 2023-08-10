FROM python:3.10

COPY . /app
WORKDIR /app

RUN pip install requests -r requirements.txt
EXPOSE 8000

CMD ["python", "manage.py", "runserver"]