# backend/Dockerfile

# Low weight python
FROM python:3.10-slim

# 2. Dont allow python to create .pyc 'n force show logs in real time
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Work directory
WORKDIR /app

# 4. Copy of reqs
COPY requirements.txt .

# 5. Install reqs
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 6. Copy whole /backend
COPY . .

# 7. Run app
CMD ["fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]