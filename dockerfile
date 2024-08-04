FROM python:3.11.9
WORKDIR /app
ENV PYTHONUNBUFFERED 1

COPY requirements1.txt .

RUN pip install -r requirements1.txt

COPY . .


EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]