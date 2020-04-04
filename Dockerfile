FROM python:3.8

ADD requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
ADD extractor.py /app

VOLUME ["/app/data/"]

CMD [ "python", "extractor.py" ]