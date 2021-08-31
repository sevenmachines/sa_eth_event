FROM python:3
RUN apt update && apt install -y libgl1-mesa-glx
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP app.py
ENV FLASK_ENV production
ENV APP_SETTINGS config.ProductionConfig
ENV AWS_DEFAULT_REGION eu-west-1
WORKDIR /app
COPY . /app/
EXPOSE 5000
RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
