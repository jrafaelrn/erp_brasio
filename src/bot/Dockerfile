FROM python:3.9

COPY . /app
WORKDIR /app

RUN pip install requests

EXPOSE 8080

CMD ["python", "main.py"]
