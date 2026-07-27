## Crible : Ore Segmentation

A comprehensive guide to setting up and running the project.
## Environment Setup & Dependency Installation

### Manual Setup (Recommended for Development)

Make sure you have **Python 3.13** installed.

#### 1. Clone this repository
```bash
git clone https://git.digilab.ocpgroup.ma/mining-analytics-platform/ore-segmentation.git
cd ore-segmentation
```

#### 2. Create a Virtual Environment
```bash
cd backend # if other place, add your venv in .gitignore
python -m venv venv
```

#### 3. Activate the Virtual Environment
- **Linux/macOS**
```bash
source venv/bin/activate
```

- **Windows**
```bash
venv\Scripts\activate
```

#### 4. Install Base Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Install PyTorch (CPU or GPU)
> Manual PyTorch install is needed depending on your hardware:

- **For CPU-only machines:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

- **For GPU (CUDA 11.8):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 6. Run the App
```bash
# Make sure you are in backend folder
python api/server.py

# or using explicit command of uvicorn
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### 🐳 Run with Docker (CPU or GPU Auto-Handled)

> Docker build handles PyTorch install conditionally based on a `TORCH` environment variable.

#### 1. Build and Run with Docker Compose
```bash
# CPU version (default)
TORCH=cpu docker-compose up --build

# GPU version (CUDA 11.8)
TORCH=gpu docker-compose up --build
```

If `TORCH` is **not set**, the image defaults to `cpu` version.

---

This setup ensures:
- A single `requirements.txt` for all environments
- Deterministic installation per machine
- Reproducible Docker builds with minimal manual config


## Frontend Setup

A separate `README.md` specific to the frontend will be added soon.

For now, follow these steps to run the frontend locally:

#### 1. Ensure Node.js is installed
- Requires **Node.js 20.x LTS**
- You can check your version:
```bash
node -v

# example: v22.14.0
```

#### 2. Navigate to the frontend directory
```bash
cd frontend
```

#### 3. Install dependencies
```bash
npm install
```

---

Once installed, follow the frontend-specific README when available for further usage and deployment instructions.


### Contact & Support

If you encounter any issues or have questions:

- Development:  
  nabil.zaim@ocpgroup.ma  
  Adnane.MIRI@ocpgroup.ma

- DevOps / Infrastructure:  
  abdelhalim.addad@ocpgroup.ma


# ⚠️ Intern Note (Draft)

_The following section is a draft intended for internal review only. Interns may ignore this content._

#### 3. Install SAM Model Checkpoint

- If the required checkpoint is missing when running inference, the function will automatically handle it for you. However, you can manually download the checkpoint by running **one** of the following commands:

```bash
cd backend
python .\sam\load_checkpoint.py --path assets/checkpoints/sam_vit_b_01ec64.pth # Basic model, sufficient for most cases
# Alternatively, choose a different model size:
python .\sam\load_checkpoint.py --path assets/checkpoints/sam_vit_l_0b3195.pth # large
python .\sam\load_checkpoint.py --path assets/checkpoints/sam_vit_h_4b8939.pth # huge
```

- **Or check Meta's GitHub SAM Link:** [Model Checkpoints](https://github.com/facebookresearch/segment-anything?tab=readme-ov-file#model-checkpoints)

#### 4. Install NVIDIA Container Toolkit on the host

- If the required checkpoint is missing when running inference, the function will automatically handle it for you. However, you can manually download the checkpoint by running **one** of the following commands:

```bash
# Configure the production repository:
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Update the packages list from the repository
sudo apt-get update

# Install the NVIDIA Container Toolkit packages:
sudo apt-get install -y nvidia-container-toolkit

#Configure the container runtime by using the nvidia-ctk command:
sudo nvidia-ctk runtime configure --runtime=docker

#Restart the Docker daemon:
sudo systemctl restart docker
```

- **Or check NVIDIA's official page for [NCT installation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

### Simulate RTSP URL for MP4 Video

To simulate an RTSP stream using an MP4 video file:

#### 1. **Run the RTSP Server:**

```bash
.\mediamtx.exe # from: https://github.com/bluenviron/mediamtx
```

#### 2. **Stream Video Using FFmpeg (input file: stream.mp4):**

```bash
ffmpeg -re -i stream.mp4 -f rtsp -rtsp_transport tcp rtsp://localhost:8554/mystream
```

### Capture Frames

Capture a **single** or **periodic** frames from the video stream:

- **Script Path:** `backend/video_capture/video_capture.py`
- **Command:**

```bash
cd backend
# helper command to get all command options
python .\video_capture\video_capture.py --help
# single frame
python .\video_capture\video_capture.py --mode single
# periodic frame, periodic is the default if mode not passed.
python .\video_capture\video_capture.py --mode periodic
```

### Run Backend server api:

```bash
cd backend
uvicorn api.server:app --reload
```

### Run Tests

Execute unit tests:

- **Test folder Path:** `backend/tests/`
- **Command:**

```bash
cd backend
pytest -v .\tests\
```

### Install Kafka

Download and install Kafka:

- **Download Link:** [Apache Kafka Binary Downloads](https://downloads.apache.org/kafka/3.8.0/kafka_2.13-3.8.0.tgz)

## Start the Kafka environment

First, add asbolute path of "/path/../kafka_2.13-3.8.0/bin" in PATH as env variable of the system.

- **Script Path:** `/path/../kafka_2.13-3.8.0/`

### Ensure Broker Configuration is Set Correctly: Ensure that your Kafka broker's server.properties file includes the following properties:

```bash
socket.request.max.bytes=104857600
message.max.bytes=104857600
max.message.bytes=104857600
```

1. **Start Zookeeper to Manage Kafka Brokers:**

- **Linux/MacOS:** `bin/zookeeper-server-start.sh config/zookeeper.properties`

- **Windows:** `.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties`

2. **Start Kafka Broker:**

- **Linux/MacOS:** `bin/kafka-server-start.sh config/server.properties`

- **Windows:** `.\bin\windows\kafka-server-start.bat .\config\server.properties`

### Create a Kafka Topic

Create a new topic in Kafka (e.g., `captured-images`):

- **Linux/MacOS:** `bin/kafka-topics.sh --create --topic captured-images --bootstrap-server localhost:9092`
- **Windows:** `bin\windows\kafka-topics.bat --create --topic captured-images --bootstrap-server localhost:9092`

### List Kafka Topics

List all topics to ensure the Kafka broker is running:

- **Linux/MacOS:** `bin/kafka-topics.sh --list --bootstrap-server localhost:9092`

- **Windows:** `bin/windows/kafka-topics.bat --bootstrap-server localhost:9092 --list`
