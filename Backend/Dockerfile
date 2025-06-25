FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for statsmodels and others
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libatlas-base-dev \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 10000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]