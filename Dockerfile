# Use the official Python image as the base image
FROM python:3.9

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# export env file
ENV ENV_FILE .env

# Create and set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files into the container
COPY . /app/

# Expose the port that the Django development server will run on
EXPOSE 8002

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]
