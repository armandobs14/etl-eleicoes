FROM python:3-alpine

WORKDIR /

COPY client.py client.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "client.py" ]