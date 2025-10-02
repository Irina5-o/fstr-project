FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Увеличиваем sleep и добавляем подробное логирование
CMD ["sh", "-c", "echo '=== STARTING CONTAINER ===' && sleep 30 && echo '=== RUNNING MIGRATIONS ===' && python manage.py migrate && echo '=== STARTING GUNICORN ===' && gunicorn fstr.wsgi:application --bind 0.0.0.0:${PORT:-8080} --access-logfile - --error-logfile - --log-level debug"]