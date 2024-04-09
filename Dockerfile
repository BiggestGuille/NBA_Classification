FROM python:3.12

WORKDIR /src

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY /data ./data
COPY /src ./src
COPY app.py .

EXPOSE 5000

CMD ["python3", "app.py"]