# Use a lightweight official base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy application files and dependencies into the container
COPY . /app 

# Install any necessary dependencies
# The --no-cache-dir flag minimizes image size by preventing pip from storing installation files
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on (optional)
EXPOSE 8000

# Define the command to run when the container starts
CMD ["python", "app.py"]