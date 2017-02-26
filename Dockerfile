FROM python:3.4

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY . .

ENV DEBUG False

EXPOSE 8000
CMD ["python", "/usr/src/app/pointdistribution/manage.py", "runserver", "0.0.0.0:8000"]