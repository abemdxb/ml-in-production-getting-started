# Deploying MinIO on AWS EC2 for GenAI Applications

If you're planning to run a GenAI application in the AWS cloud, follow this beginner-friendly guide to set up MinIO on an EC2 instance using Ubuntu 22.04 LTS.

## Why Ubuntu 22.04 LTS for GenAI?
Ubuntu 22.04 LTS is an excellent choice for AI/ML workloads because it offers:
- Excellent compatibility with popular AI frameworks (TensorFlow, PyTorch, Hugging Face)
- Long-term support until 2027
- Regular security updates
- Large community and extensive documentation

## Step 1: Launch an EC2 Instance with Ubuntu 22.04 LTS
1. Log in to your AWS Management Console (https://console.aws.amazon.com)
2. In the search bar at the top, type "EC2" and select it from the dropdown
3. Click the orange "Launch instance" button
4. **Name your instance**: Enter a descriptive name like "MinIO-GenAI-Server"
5. **Choose an AMI**:
   - Under "Application and OS Images", find "Ubuntu" in the Quick Start section
   - Select "Ubuntu Server 22.04 LTS (HVM), SSD Volume Type"
6. **Select an instance type**:
   - For testing/development: t2.large or t3.large (2 vCPUs, 8 GB RAM)
   - For production with GPU (recommended for GenAI): g4dn.xlarge
   - Note: You can change the instance type later if needed
7. **Create a key pair** (required for SSH access):
   - Click "Create new key pair"
   - Name it something memorable like "minio-genai-key"
   - Keep the default key pair type (RSA) and format (.pem for macOS/Linux or .ppk for Windows)
   - Click "Create key pair" and save the file securely on your computer
8. **Configure network settings**:
   - Keep the default VPC and subnet
   - Enable "Auto-assign public IP"
   - Create a security group with the following rules:
     - Allow SSH (port 22) from your IP address
     - Allow Custom TCP (port 9000) from your IP address (for MinIO API)
     - Allow Custom TCP (port 9090) from your IP address (for MinIO Console)
9. **Configure storage**:
   - Increase the default storage to at least 30GB (or more depending on your data needs)
   - Keep the default gp2 volume type
10. **Review and launch**:
    - Review all settings
    - Click "Launch instance"
    - You'll see a success message with a link to your instance ID

## Step 2: Connect to Your EC2 Instance

### For Windows Users:
1. Download and install PuTTY if you don't have it (https://www.putty.org/)
2. Convert your .pem key to .ppk format using PuTTYgen if you didn't download the .ppk format
3. Open PuTTY and enter your instance's Public DNS or IP in the Host Name field
4. In the left sidebar, navigate to Connection > SSH > Auth > Credentials
5. Browse and select your .ppk key file
6. Click "Open" to connect
7. When prompted for a username, enter: `ubuntu`

### For macOS/Linux Users:
1. Open Terminal
2. Change permissions for your key file:
   ```bash
   chmod 400 /path/to/your-key.pem
   ```
3. Connect using SSH:
   ```bash
   ssh -i /path/to/your-key.pem ubuntu@your-instance-public-dns
   ```
   (Replace "your-instance-public-dns" with the actual Public DNS value from your EC2 dashboard)

## Step 3: Update System and Install Docker
Once connected to your EC2 instance, run these commands:

```bash
# Update package lists and upgrade existing packages
sudo apt update
sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io

# Start Docker and enable it to start on boot
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group so you can run docker commands without sudo
sudo usermod -a -G docker ubuntu

# Apply the group change (this will disconnect you)
exit
```

Reconnect to your instance using the same SSH command from Step 2.

## Step 4: Create Configuration Files for MinIO
```bash
# Create directories for MinIO data and configuration
mkdir -p ~/minio/data
mkdir -p ~/minio/config

# Create the environment configuration file
cat > ~/minio/config/config.env << EOF
# MinIO root credentials - CHANGE THESE for security!
MINIO_ROOT_USER=myminioadmin
MINIO_ROOT_PASSWORD=minio-secret-key-change-me

# Storage volume
MINIO_VOLUMES="/data"

# Console settings
MINIO_OPTS="--console-address :9090"
EOF
```

## Step 5: Run MinIO Container
```bash
docker run -d \
  --name minio \
  --restart always \
  -p 9000:9000 -p 9090:9090 \
  -v ~/minio/data:/data \
  -v ~/minio/config/config.env:/etc/config.env \
  -e "MINIO_CONFIG_ENV_FILE=/etc/config.env" \
  minio/minio server /data
```

Verify the container is running:
```bash
docker ps
```
You should see your MinIO container in the list.

## Step 6: Access MinIO Console
1. In your AWS EC2 dashboard, find your instance's Public IPv4 address or Public DNS
2. Open a web browser and navigate to:
   ```
   http://your-instance-public-dns:9090
   ```
   (Replace "your-instance-public-dns" with your actual Public DNS or IP address)

3. Log in with the credentials you set in the config.env file:
   - Username: myminioadmin
   - Password: minio-secret-key-change-me

## Step 7: Install and Configure MinIO Client (mc)
```bash
# Download the MinIO Client
wget https://dl.min.io/client/mc/release/linux-amd64/mc

# Make it executable
chmod +x mc

# Move it to a directory in your PATH
sudo mv mc /usr/local/bin/

# Configure MinIO Client with your server
mc alias set myminio http://localhost:9000 myminioadmin minio-secret-key-change-me
```

## Step 8: Basic MinIO Operations
```bash
# Create a bucket for your GenAI application data
mc mb myminio/genai-data

# Upload a test file
echo "Hello MinIO on AWS EC2" > test-file.txt
mc cp test-file.txt myminio/genai-data/

# List objects in your bucket
mc ls myminio/genai-data/
```

## Step 9: Integrating MinIO with Your GenAI Application
For Python-based GenAI applications, you can use the MinIO Python client:

```bash
# Install the MinIO Python client
pip install minio
```

Example Python code to connect to your MinIO server:
```python
from minio import Minio

# Initialize MinIO client
client = Minio(
    "your-instance-public-dns:9000",  # Replace with your instance's public DNS or IP
    access_key="myminioadmin",
    secret_key="minio-secret-key-change-me",
    secure=False  # Set to True if you configure TLS
)

# Check if a bucket exists
if not client.bucket_exists("genai-data"):
    client.make_bucket("genai-data")

# Upload a model file
client.fput_object(
    "genai-data", "model.pkl", "/path/to/your/model.pkl"
)

# Download a model file
client.fget_object(
    "genai-data", "model.pkl", "/path/to/download/model.pkl"
)
```

## Security Best Practices for Production
1. **Enable HTTPS/TLS** for secure connections
2. **Use strong, unique passwords** for MinIO credentials
3. **Restrict security group rules** to only necessary IPs
4. **Set up regular backups** of your MinIO data
5. **Update your EC2 instance** regularly with security patches
6. **Consider using IAM roles** instead of hardcoded credentials

## Troubleshooting Tips
- If you can't connect to MinIO, check your EC2 security group rules
- If MinIO container doesn't start, check Docker logs: `docker logs minio`
- If you get permission errors, verify your MinIO credentials
- If you need to restart MinIO: `docker restart minio`
