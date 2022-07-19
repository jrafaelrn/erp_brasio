FROM python:3.9

COPY . /app

WORKDIR /app

RUN ls -la
RUN pip install requests

COPY ./credentials/keys.py /app/credentials/keys.py

CMD ["python", "main.py"]
