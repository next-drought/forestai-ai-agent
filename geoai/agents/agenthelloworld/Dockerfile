# Use an official Python runtime as a parent image
FROM mirror.gcr.io/library/python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker layer caching
COPY geoai/agents/agenthelloworld/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY geoai/agents/agenthelloworld/ .

# Make port 8080 available
EXPOSE 8080

# Run the server when the container launches
# Note: The module path is now simpler because we copied the code to the root of WORKDIR
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]