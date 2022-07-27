FROM python:3.9

COPY . /app
WORKDIR /app

RUN pip install requests google-cloud-pubsub Pillow opencv-python


ENV PORT 8080
EXPOSE 8080

CMD ["python", "main.py"]
