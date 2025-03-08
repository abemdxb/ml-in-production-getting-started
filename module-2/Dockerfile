# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory (optional)
WORKDIR /app

# Expose a port (e.g., 8000)
EXPOSE 8000

# Use Python's built-in HTTP server to serve the current directory
CMD ["python", "-m", "http.server", "8000"]