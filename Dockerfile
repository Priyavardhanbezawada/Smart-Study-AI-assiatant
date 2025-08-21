# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Update package lists and install Tesseract OCR and other dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Make port 8501 available to the world outside this container (for Streamlit)
EXPOSE 8501

# Define the command to run your app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
