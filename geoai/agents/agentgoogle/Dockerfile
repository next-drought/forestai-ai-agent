# Use an official Python runtime as a parent image
FROM mirror.gcr.io/library/python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# No heavy system deps needed for this isolated service

# Copy only the requirements file first to leverage Docker layer caching
COPY geoai/agents/agentgoogle/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the agentgoogle application code
COPY geoai/agents/agentgoogle/ .

# Make port 8080 available
EXPOSE 8080

# Run server when the container launches
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
