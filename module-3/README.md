<<<<<<< HEAD
# Module 3 practice 

Written with the help of ChatGPT (verified via deployment)

# Deploying MinIO

This document provides instructions for deploying MinIO using three different approaches: **Local**, **Docker**, and **Kubernetes (K8S)**. Choose the option that best suits your environment.

---

## Table of Contents
- [Local Deployment](#local-deployment)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
  - [Standalone Deployment](#standalone-deployment)
  - [Distributed Deployment](#distributed-deployment)
- [Additional Considerations](#additional-considerations)

---

## SECTION 1: Local Deployment

MinIO can be deployed locally in a Single-Node Single-Drive (SNSD) configuration for early development and evaluation by downloading the executable and running it directly. This is useful for development and testing.


Note that according to the MinIO page (see below),  SNSD deployments use a zero-parity erasure coded backend that provides no added reliability or availability beyond what the underlying storage volume implements. These deployments are best suited for local testing and evaluation, or for small-scale data workloads that do not have availability or performance requirements.


### Steps for Windows

1. **Download the MinIO Binary**  
   Visit the [MinIO Page](https://min.io/docs/minio) and download the appropriate binary or executable for your operating system.

   I used https://dl.min.io/server/minio/release/windows-amd64/minio.exe for Windows

2. **Start the Server and prep the path for Storage**

   Create `/path/to/data` with the directory where you want to store data and ensure it's empty including hidden folders. I used `/Minio` in this repository.

   Open a powershell and run:

   ``` 
   minio.exe server D:/minio --console-address ":9090"
   ```

   The output should resemble the following:

   ``` 
    Status:         1 Online, 0 Offline.
    API: http://192.168.2.100:9000  http://127.0.0.1:9000
    Console: http://192.168.2.100:9090 http://127.0.0.1:9090

    Command-line: https://min.io/docs/minio/linux/reference/minio-mc.html
    $ mc alias set myminio http://10.0.2.100:9000 minioadmin minioadmin

    Documentation: https://min.io/docs/minio/linux/index.html
   ``` 

    The API block lists the network interfaces and port on which clients can access the MinIO S3 API. The Console block lists the network interfaces and port on which clients can access the MinIO Web Console.

3. **Install the mc CLI and create an alias for the local MinIO deployment** 
    Installation first! 
    
    Open the following file in a browser:
    ``` 
    https://dl.min.io/client/mc/release/windows-amd64/mc.exe
    ``` 

    Execute the file by double clicking on it, or by running the following in the command prompt or powershell:

    ``` 
    \path\to\mc.exe --help
    ``` 
    Now create a new alias corresponding to the MinIO deployment. Specify any of the hostnames or IP addresses from the MinIO Server API block, such as http://localhost:9000.


    If you want to run mc from any directory without prefixing .\, do the following:

    Press Windows Key → type “env” → select Edit the system environment variables.
    Click Environment Variables..., then under System variables, edit Path.
    Add the folder containing mc.exe (e.g., C:\Tools\minio\) to the Path.
    Restart your PowerShell or VS Code to pick up the change.
    Otherwise replace the below `mc` commands with  with `.\mc.exe`
    

    ```
    mc alias set myminio http://localhost:9000 myminioadmin minio-secret-key-change-me
    ```

    Replace `myminio` with the desired name to use for the alias.
    Replace `myminioadmin` with  `minioadmin` (standard for the local version in Windows)
    Replace `minio-secret-key-change-me` with `minioadmin` (standard for the local version in Windows)
    You can then interact with the container using any `mc` command. If your local host firewall permits external access to the MinIO S3 API port, other hosts on the same network can access the MinIO deployment using the IP or hostname for your local host.

4. **Access the Console**  
   Open your browser and go to:  
   ```
   http://localhost:9090
   ```

5. **Play Around**  
   Do the following through the console for practice  

    1. Create a Bucket
        ```sh
        mc mb myminio/new-bucket
        Creates a new bucket named new-bucket.
        ```
    2. Upload (Create) an Object
        ```sh
        mc cp .\local-file.txt myminio/new-bucket
        Copies (uploads) local-file.txt from your current directory to new-bucket.
        ```
    3. List (Read) Objects in a Bucket
        ```sh
        mc ls myminio/new-bucket
        Shows all objects in new-bucket.
        ```

    4. Download (Update/Read) an Object
        ```sh
        mc cp myminio/new-bucket/local-file.txt .\
        Copies (downloads) local-file.txt from new-bucket back to the current directory.
        ```

    5. Remove (Delete) an Object
        ```sh
        mc rm myminio/new-bucket/local-file.txt
        Deletes local-file.txt from new-bucket.
        ```

    6. (Optional) To remove the bucket itself once it’s empty:
        ```sh
        mc rb myminio/new-bucket
        These commands give you a quick start on essential bucket and object operations
        ```
---

## Section 2: Docker Deployment

Docker provides a containerized approach to running MinIO.

### Steps

1. **Pull the MinIO Docker Image**  
   ```sh
   docker pull docker://minio/minio

   ```
2. **Create the Environment Variable File**
    Create an environment variable file at /etc/default/minio. For Windows hosts, specify a Windows-style path similar to C:\minio\config. The MinIO Server container can use this file as the source of all environment variables.

    The following example provides a starting environment file:
    ```sh
        # MINIO_ROOT_USER and MINIO_ROOT_PASSWORD sets the root account for the MinIO server.
        # This user has unrestricted permissions to perform S3 and administrative API operations on any resource in the deployment.
        # Omit to use the default values 'minioadmin:minioadmin'.
        # MinIO recommends setting non-default values as a best practice, regardless of environment

        
        #MINIO_ROOT_USER=myminioadmin
        #MINIO_ROOT_PASSWORD=minio-secret-key-change-me

        # MINIO_VOLUMES sets the storage volume or path to use for the MinIO server.

        MINIO_VOLUMES="/mnt/data"

        # MINIO_OPTS sets any additional commandline options to pass to the MinIO server.
        # For example, `--console-address :9090` sets the MinIO Console listen port
        MINIO_OPTS="--console-address :9090"
    ```
    Include any other environment variables as required for your deployment.

3. **Run the Container and check status**  

    I had trouble running this is powershell so switched over to gitbash and ran the below:

    ```sh
    docker run -dt \
    -p 9000:9000 -p 9090:9090 \
    -v "c:/Users/abemd/Documents/ML Experiments/ML_in_Prod/ml-in-production-getting-started/module-3/minio_data:/mnt/data" \
    -v "c:/Users/abemd/Documents/ML Experiments/ML_in_Prod/ml-in-production-getting-started/module-3/config.env:/etc/config.env" \
    -e "MINIO_CONFIG_ENV_FILE=/etc/config.env" \
    --name "minio_local" \
    minio/minio server /mnt/data
    ```

    ```sh
        docker logs minio_local
    ```

3. **Access MinIO**  
   Console: [http://localhost:9090](http://localhost:9090)
   You can access the MinIO deployment over a Terminal or Shell using the MinIO Client (mc). See MinIO Client Installation Quickstart for instructions on installing mc.

    Create a new alias corresponding to the MinIO deployment. Use a hostname or IP address for your local machine along with the S3 API port 9000 to access the MinIO deployment. Any traffic to that port on the local host redirects to the container.
    
    ```sh
        mc alias set minio-alias http://localhost:9000 myminioadmin minio-secret-key-change-me
    ```
    Replace `minio-alias` with the alias name to create for this deployment.

    Replace `myminioadmin` and `minio-secret-key-change-me` with the `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` values in the environment file specified to the container or use `minioadmin` for both if you did not define either.

    you can now use the mc commands as per the local file experiments above


    **SIDE NOTE A:**  If you're building in AWS cloud as opposed to locally, follow our [Comprehensive Guide for Deploying MinIO on AWS EC2](AWS_EC2_DEPLOYMENT.md). This guide includes step-by-step instructions for setting up MinIO on Ubuntu 22.04 LTS, specifically optimized for GenAI applications.



---

## Section 3: Kubernetes Deployment

This section provides step-by-step instructions for deploying MinIO in a local Minikube environment on your laptop.

### Prerequisites

- Minikube installed on your laptop
- kubectl configured to use Minikube
- Basic understanding of Kubernetes concepts

### Step 1: Start Minikube

Ensure Minikube is running with sufficient resources:

```bash
# Check if Minikube is running
minikube status

# If not running, start it with appropriate resources for your laptop
minikube start --cpus=2 --memory=4096 --disk-size=20g

# Verify Minikube is running
minikube status
```

### Step 2: Create the MinIO Persistent Volume Claim

Create `minio-pvc.yaml`:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: minio-pv-claim
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 10Gi
```

Apply the PVC:
```bash
# Apply the PVC configuration
kubectl apply -f minio-pvc.yaml

# Verify the PVC was created
kubectl get pvc
```

### Step 3: Deploy MinIO

Create `minio-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minio-deployment
spec:
  selector:
    matchLabels:
      app: minio
  replicas: 1
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
      - name: minio
        image: minio/minio:latest
        args:
          - server
          - /data
        env:
          - name: MINIO_ACCESS_KEY
            value: "minio"
          - name: MINIO_SECRET_KEY
            value: "minio123"
        ports:
          - containerPort: 9000
          - containerPort: 9090
        volumeMounts:
          - name: minio-storage
            mountPath: /data
      volumes:
      - name: minio-storage
        persistentVolumeClaim:
          claimName: minio-pv-claim
```

Apply the deployment:
```bash
# Apply the deployment configuration
kubectl apply -f minio-deployment.yaml

# Verify the deployment was created
kubectl get deployments

# Check if the pod is running
kubectl get pods
```

### Step 4: Create the MinIO Service

Create `minio-service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: minio-service
spec:
  type: NodePort
  ports:
    - name: api
      port: 9000
      targetPort: 9000
      nodePort: 30900
    - name: console
      port: 9090
      targetPort: 9090
      nodePort: 30909
  selector:
    app: minio
```

Apply the service:
```bash
# Apply the service configuration
kubectl apply -f minio-service.yaml

# Verify the service was created
kubectl get services
```

### Step 5: Access MinIO

There are multiple ways to access the MinIO service:

#### Option 1: Using minikube service

```bash
# This will open the MinIO API endpoint in your default browser
minikube service minio-service --url
```

You should see two URLs:
- First URL (port 30900): MinIO API endpoint
- Second URL (port 30909): MinIO Console

#### Option 2: Using port-forwarding

```bash
# Forward the MinIO API port to your local machine
kubectl port-forward svc/minio-service 9000:9000

# In a new terminal, forward the MinIO Console port
kubectl port-forward svc/minio-service 9090:9090
```

Then access:
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9090

### Step 6: Log in to MinIO Console

1. Open the MinIO Console URL in your browser
2. Log in with the following credentials:
   - Username: minio
   - Password: minio123

### Step 7: Create a Bucket and Upload Files

1. In the MinIO Console, click "Create Bucket"
2. Enter a bucket name (e.g., "my-bucket") and click "Create Bucket"
3. Click on the newly created bucket
4. Click "Upload" to upload files to the bucket

### Step 8: Use MinIO with the MinIO Client (mc)

```bash
# Install the MinIO Client if you haven't already
# For Windows:
# Download from https://dl.min.io/client/mc/release/windows-amd64/mc.exe

# Configure the MinIO Client
mc alias set myminio http://$(minikube ip):30900 minio minio123

# List buckets
mc ls myminio

# Upload a file
mc cp myfile.txt myminio/my-bucket/

# Download a file
mc cp myminio/my-bucket/myfile.txt ./
```

### Troubleshooting

#### Pod not starting
```bash
# Check pod status
kubectl get pods

# Get detailed information about the pod
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>
```

#### Cannot access MinIO
```bash
# Check if the service is running
kubectl get svc minio-service

# Check Minikube IP
minikube ip

# Ensure you're using the correct URL
echo "MinIO API: http://$(minikube ip):30900"
echo "MinIO Console: http://$(minikube ip):30909"
```

### Cleanup

When you're done, you can clean up the resources:

```bash
# Delete the service
kubectl delete -f minio-service.yaml

# Delete the deployment
kubectl delete -f minio-deployment.yaml

# Delete the PVC
kubectl delete -f minio-pvc.yaml

# Stop Minikube (optional)
minikube stop
```

**SIDE NOTE 2:**  For deploying MinIO on AWS EC2 with Kubernetes, check our [Comprehensive Guide for Kubernetes Deployment on AWS EC2](KUBERNETES_EC2_DEPLOYMENT.md). This guide provides detailed instructions for both standalone and distributed MinIO deployments using Kubernetes on AWS EC2 instances.

---

## Additional Considerations from ChatGPT

- **Security:** Update `MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY`. Consider using TLS.
- **Scaling:** Adjust replicas in the StatefulSet for distributed deployments.
- **Cleanup:** Remove resources when done:
  ```sh
  kubectl delete deployment minio-deployment
  kubectl delete pvc minio-pv-claim
  kubectl delete svc minio-service
  kubectl delete statefulset minio
  kubectl delete svc minio
  ```

By following these instructions, you can deploy MinIO using local, Docker, or Kubernetes methods depending on your needs.
