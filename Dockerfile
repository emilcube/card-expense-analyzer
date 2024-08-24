FROM python:3.12-slim

WORKDIR /app

# dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy data
COPY src/ ./src/
COPY config.yaml .
COPY session_name.session .
#COPY data/ ./data/

# port for dash
EXPOSE 8050  

CMD ["python", "src/main.py"]
