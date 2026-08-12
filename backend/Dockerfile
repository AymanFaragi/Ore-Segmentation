# syntax=docker/dockerfile:1

# =========================================================================
# Stage 1: builder
# Installs build-only tooling (git, compilers) and resolves all Python deps
# into a --user site-packages dir. None of this lands in the runtime image.
# =========================================================================
FROM python:3.13-slim-bullseye AS builder

# 'cpu' (default) or 'gpu' — selects the PyTorch wheel index below.
ARG TORCH=cpu
RUN if [ "$TORCH" != "cpu" ] && [ "$TORCH" != "gpu" ]; then \
        echo "Invalid TORCH value: $TORCH. Valid options are 'cpu' or 'gpu'." && exit 1; \
    fi

# git is needed only to resolve the `segment_anything @ git+https://...`
# requirement at install time; build-essential covers any package that
# needs to compile a C extension. Neither survives into the runtime stage.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

RUN pip install --upgrade pip

RUN if [ "$TORCH" = "cpu" ]; then \
        pip install --user torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu; \
    else \
        pip install --user torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124; \
    fi

COPY requirements.txt .
RUN pip install --user -r requirements.txt


# =========================================================================
# Stage 2: runtime
# Only what's needed to actually run the FastAPI/SAM service.
# =========================================================================
FROM python:3.13-slim-bullseye AS runtime

# Runtime-only system libs: OpenCV needs libgl1/libglib2, video_capture.py
# shells ffmpeg for RTSP handling. No git, no compilers.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser \
    && usermod -aG video appuser \
    && mkdir -p /app \
    && chown -R appuser:appgroup /app

WORKDIR /app/backend

# Bring over the resolved --user site-packages from the builder stage and
# hand ownership to appuser (COPY --chown handles this in one step, so no
# extra `chown -R` layer walking the whole tree is needed afterward).
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local

ENV PATH="/home/appuser/.local/bin:${PATH}" \
    PYTHONPATH="/app:/app/backend" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENV NVIDIA_VISIBLE_DEVICES=${NVIDIA_VISIBLE_DEVICES:-all} \
    NVIDIA_DRIVER_CAPABILITIES=${NVIDIA_DRIVER_CAPABILITIES:-compute,utility}

# --chown here is what actually matters: without it this COPY writes
# root:root regardless of the USER instruction below, which previously
# broke config.yaml writes from /update_dimensions/.
COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 8000

# Hits the existing GET /dimensions/ endpoint — no new route needed.
# Long start-period because SAM model + checkpoint loading at boot is slow.
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/dimensions/', timeout=3)" || exit 1

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
