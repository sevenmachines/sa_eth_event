FROM python:3
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app
COPY . /app/
CMD ["python", "app.py"]
