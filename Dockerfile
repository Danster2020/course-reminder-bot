FROM python:3.12-slim

# Set working directory
WORKDIR /src/app

# Install uv once at build time
RUN pip install uv

# Copy your app code and env file into the image
COPY app/ /src/app
COPY stack.env /src/stack.env

# Default command
CMD ["uv", "run", "main.py"]