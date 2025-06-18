FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright + Chromium
RUN apt-get update && apt-get install -y \
    wget curl gnupg2 unzip fonts-liberation libnss3 libatk-bridge2.0-0 \
    libgtk-3-0 libxss1 libasound2 libgbm-dev libxshmfence1 libxrandr2 \
    libu2f-udev libvulkan1 libxdamage1 libxi6 libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Install Playwright browsers (correct command for Python)
RUN python -m playwright install --with-deps

# Copy app source code
COPY . .

# Expose FastAPI port
EXPOSE 8080


# Start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]


# Run the batch job (change as needed for Cloud Run service)
# CMD ["python", "-m", "app.run_job"]