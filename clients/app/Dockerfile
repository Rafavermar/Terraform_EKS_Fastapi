FROM python:3.11
WORKDIR /app
COPY src /app/
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
