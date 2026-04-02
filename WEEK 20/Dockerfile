# Use slim version of Python for smaller image size (better for scalability and cold-starts)
FROM python:3.10-slim

# Set the working directory in the Docker container
WORKDIR /app

# Install curl for the HEALTHCHECK
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies securely
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Add a healthcheck to ensure the container is responsive (critical for load balancers in AWS/Heroku)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the Streamlit app on all interfaces (0.0.0.0) so it's accessible externally
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
