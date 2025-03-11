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

## Local Deployment

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
    Console: http://192.168.2.100:9001 http://127.0.0.1:9001

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
   http://localhost:9001
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
        .\mc.exe rm myminio/new-bucket/local-file.txt
        Deletes local-file.txt from new-bucket.
        ```

    6. (Optional) To remove the bucket itself once it’s empty:
        ```sh
        .\mc.exe rb myminio/new-bucket
        These commands give you a quick start on essential bucket and object operations
        ```
---

## Docker Deployment

Docker provides a containerized approach to running MinIO.

### Steps

1. **Pull the MinIO Docker Image**  
   ```sh
   docker pull docker://minio/minio

   ```
2. **Create the Environment Vairable File**
    Create an environment variable file at /etc/default/minio. For Windows hosts, specify a Windows-style path similar to C:\minio\config. The MinIO Server container can use this file as the source of all environment variables.

    The following example provides a starting environment file:
    ```sh
        # MINIO_ROOT_USER and MINIO_ROOT_PASSWORD sets the root account for the MinIO server.
        # This user has unrestricted permissions to perform S3 and administrative API operations on any resource in the deployment.
        # Omit to use the default values 'minioadmin:minioadmin'.
        # MinIO recommends setting non-default values as a best practice, regardless of environment

        MINIO_ROOT_USER=myminioadmin
        MINIO_ROOT_PASSWORD=minio-secret-key-change-me

        # MINIO_VOLUMES sets the storage volume or path to use for the MinIO server.

        MINIO_VOLUMES="/mnt/data"

        # MINIO_OPTS sets any additional commandline options to pass to the MinIO server.
        # For example, `--console-address :9001` sets the MinIO Console listen port
        MINIO_OPTS="--console-address :9001"
    ```
    Include any other environment variables as required for your deployment.

3. **Run the Container and check status**  
    ```sh
        docker run -dt                                
        -p 9000:9000 -p 9001:9001                     
        -v PATH:/mnt/data                             
        -v /etc/default/minio:/etc/config.env         
        -e "MINIO_CONFIG_ENV_FILE=/etc/config.env"    
        --name "minio_local"                          
        minio server --console-address ":9001"
    ```
    ```sh
        docker logs minio
    ```



3. **Access MinIO**  
   Console: [http://localhost:9001](http://localhost:9001)
   You can access the MinIO deployment over a Terminal or Shell using the MinIO Client (mc). See MinIO Client Installation Quickstart for instructions on installing mc.

    Create a new alias corresponding to the MinIO deployment. Use a hostname or IP address for your local machine along with the S3 API port 9000 to access the MinIO deployment. Any traffic to that port on the local host redirects to the container.
    
    ```sh
        mc alias set minio-alias http://localhost:9000 myminioadmin minio-secret-key-change-me
    ```
    Replace `minio-alias` with the alias name to create for this deployment.

    Replace `myminioadmin` and `minio-secret-key-change-me` with the `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` values in the environment file specified to the container.
---

## Kubernetes Deployment

Ensure you have a running Kubernetes cluster and `kubectl` installed before proceeding.

### Standalone Deployment

#### Step 1: Create a Persistent Volume Claim (PVC)
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
```sh
kubectl apply -f minio-pvc.yaml
```

#### Step 2: Create the MinIO Deployment
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
        volumeMounts:
          - name: minio-storage
            mountPath: /data
      volumes:
      - name: minio-storage
        persistentVolumeClaim:
          claimName: minio-pv-claim
```
Apply the deployment:
```sh
kubectl apply -f minio-deployment.yaml
```

#### Step 3: Create a Service
Create `minio-service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: minio-service
spec:
  type: LoadBalancer
  ports:
    - port: 9000
      targetPort: 9000
  selector:
    app: minio
```
Apply the service:
```sh
kubectl apply -f minio-service.yaml
```

### Distributed Deployment

#### Step 1: Create a Headless Service
Create `minio-headless.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: minio
spec:
  clusterIP: None
  ports:
    - port: 9000
  selector:
    app: minio
```
Apply:
```sh
kubectl apply -f minio-headless.yaml
```

#### Step 2: Create the MinIO StatefulSet
Create `minio-statefulset.yaml`:
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: minio
spec:
  serviceName: minio
  replicas: 4
  selector:
    matchLabels:
      app: minio
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
          - http://minio-0.minio.default.svc.cluster.local/data
          - http://minio-1.minio.default.svc.cluster.local/data
          - http://minio-2.minio.default.svc.cluster.local/data
          - http://minio-3.minio.default.svc.cluster.local/data
        env:
          - name: MINIO_ACCESS_KEY
            value: "minio"
          - name: MINIO_SECRET_KEY
            value: "minio123"
        ports:
          - containerPort: 9000
        volumeMounts:
          - name: data
            mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes:
        - ReadWriteOnce
      storageClassName: standard
      resources:
        requests:
          storage: 10Gi
```
Apply:
```sh
kubectl apply -f minio-statefulset.yaml
```

#### Step 3: Expose the Service
Apply `minio-service.yaml` again:
```sh
kubectl apply -f minio-service.yaml
```

---

## Additional Considerations

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