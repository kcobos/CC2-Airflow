FROM python:3.8

EXPOSE 8080

# Install pip requirements
ADD requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
ADD core /app/core
ADD app.py /app
ADD test_app.py /app

CMD ["gunicorn", "--timeout", "3600", "--bind", "0.0.0.0:8080", "app:app"]
