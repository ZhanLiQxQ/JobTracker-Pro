# Use Playwright officially recommended image, includes all browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt .

# Install dependencies
# --no-cache-dir option can reduce the final image size
RUN pip install --no-cache-dir -r requirements.txt

COPY ./model_data ./model_data
# Copy all application code (including fine-tuned model folder)
COPY *.py .

# Expose Flask service port
EXPOSE 5000

# Command to run when container starts
CMD ["python", "api.py"]