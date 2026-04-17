# FROM python:3.11

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir -r requirements.txt

# RUN python manage.py collectstatic --noinput

# CMD ["gunicorn", "fedsecure.wsgi:application", "--bind", "0.0.0.0:8000"]




# FROM python:3.11

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir -r requirements.txt

# # Set environment variable for Django
# ENV PYTHONUNBUFFERED=1

# # Collect static safely
# # RUN python manage.py collectstatic --noinput 

# # CMD python manage.py migrate && python manage.py collectstatic --noinput && gunicorn fedsecure.wsgi:application --bind 0.0.0.0:8000

# # CMD ["gunicorn", "fedsecure.wsgi:application", "--bind", "0.0.0.0:8000"]

# CMD ["bash", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn fedsecure.wsgi:application --bind 0.0.0.0:8000"]







FROM python:3.11

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1

# Use Render dynamic port
CMD ["bash", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn fedsecure.wsgi:application --bind 0.0.0.0:$PORT"]