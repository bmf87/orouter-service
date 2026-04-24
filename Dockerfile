FROM python:3.11-slim

# Prevent writing .pyc files and holding/buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install only minimal runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with user ID 1000
# Hugging Face Spaces strictly runs containers as user 1000
RUN useradd -m -u 1000 user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Change working directory to the user's application path
WORKDIR $HOME/app

# Copy requirements and transfer ownership to the user
COPY --chown=user:user requirements.txt .

# Switch to the new user before installing dependencies
USER user

# Install Python packages (llama-cpp-python pulls pre-built CUDA wheel - no compilation!)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=user:user . .

# Expose the port HF expects (default 7860)
EXPOSE 7860

# Start FastAPI with uvicorn on port 7860
CMD ["uvicorn", "ors.app.main:app", "--host", "0.0.0.0", "--port", "7860"]