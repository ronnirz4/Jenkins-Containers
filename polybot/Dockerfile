FROM python:3.10.12-slim-bullseye
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install scikit-learn
COPY . .
ENV FLASK_APP=app.py
EXPOSE 8443

CMD ["flask", "run"]