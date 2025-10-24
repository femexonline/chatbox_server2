# Use lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the WebSocket port
EXPOSE 8080

# Command to run the WebSocket server
CMD ["python3", "server2.py"]