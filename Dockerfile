FROM python:3.10-slim

WORKDIR /app

COPY requirements.lock ./
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock

COPY src ./src

ENTRYPOINT ["python3", "src/collect.py", "-gv", "--notime", "--clean"]