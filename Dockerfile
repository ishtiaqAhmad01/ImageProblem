# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Collect static files (optional if you use static)
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start the app using gunicorn
CMD ["gunicorn", "ImageProblem.wsgi:application", "--bind", "0.0.0.0:8000"]