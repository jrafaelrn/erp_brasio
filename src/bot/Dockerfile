FROM python:3.9

COPY . /app
WORKDIR /app

RUN pip install requests

ENV PORT 8080
EXPOSE 8080

CMD ["python", "main.py"]
