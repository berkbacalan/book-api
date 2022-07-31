# Pull base image
FROM python:3.10-slim-buster as builder
# Set environment variables

# Install dependencies
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

FROM builder as final
WORKDIR /app
COPY ./app/ /app/app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]