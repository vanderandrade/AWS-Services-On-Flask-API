FROM python:3.7


WORKDIR /usr/src/app

COPY ~/.aws .

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["app.py"]