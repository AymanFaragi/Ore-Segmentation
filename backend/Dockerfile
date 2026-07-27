FROM python:3.13-slim-bullseye

WORKDIR /app/backend

# Build argument to select requirements file: 'cpu' (default) or 'gpu'
ARG TORCH=cpu

# Validate the TORCH value; only 'cpu' or 'gpu' are allowed.
RUN if [ "$TORCH" != "cpu" ] && [ "$TORCH" != "gpu" ]; then \
    echo "Invalid TORCH value: $TORCH. Valid options are 'cpu' or 'gpu'." && exit 1; \
    fi

# Conditionally install torch, torchvision, and torchaudio
RUN if [ "$TORCH" = "cpu" ]; then \
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu; \
    else \
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124; \
    fi

# Install git and required libraries
RUN apt-get update && \
    apt-get install -y git libgl1-mesa-glx && \
    apt-get install -y libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/* 

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN apt-get update && apt-get install -y ffmpeg
# # Copy the appropriate requirements file based on the TORCH argument
# COPY requirements_${TORCH}.txt /tmp/requirements.txt

# RUN pip install --upgrade pip && pip install -r requirements.txt
# Copy the rest of your application code


RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app


USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/backend" 

# Set CUDA related environment variables for GPU usage
ENV NVIDIA_VISIBLE_DEVICES=${NVIDIA_VISIBLE_DEVICES:-all} \
    NVIDIA_DRIVER_CAPABILITIES=${NVIDIA_DRIVER_CAPABILITIES:-compute,utility}

COPY . .
EXPOSE 8000
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
