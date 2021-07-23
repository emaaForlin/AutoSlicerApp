FROM python:3.8-alpine
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev
WORKDIR /App
COPY . .
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
EXPOSE 5000
#CMD ["venv/bin/python", "/App/backend/entrypoint.py"]

