# Use the official Python base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the requirements file to the working directory
COPY ./requirements.txt /usr/src/app/requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade -r /usr/src/app/requirements.txt

# Copy the application code to the working directory
COPY . /usr/src/app

# Expose the port that FastAPI will run on
EXPOSE 80

# Command to run the application with Uvicorn ASGI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
