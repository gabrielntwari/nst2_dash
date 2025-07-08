# Dockerfile
FROM python:3.11 

# Set up a new user named "user" with user ID 1000 for security best practices
RUN useradd -m -u 1000 user
USER user

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY --chown=user . .

# Expose the port (Hugging Face Spaces automatically uses 7860 if you don't specify app_port in README.md)
EXPOSE 7860

# Command to run your Dash application with Gunicorn
CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:7860", "--workers", "5"]
