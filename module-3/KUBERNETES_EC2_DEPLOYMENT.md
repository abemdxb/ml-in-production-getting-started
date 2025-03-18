# Deploying MinIO on AWS EC2 with Kubernetes

This guide provides comprehensive instructions for deploying MinIO on AWS EC2 instances using Kubernetes, covering both standalone and distributed deployment options.

> **Beginner's Note:** 
> - **What is Kubernetes?** Kubernetes (K8s) is an open-source platform for automating deployment, scaling, and management of containerized applications. Think of it as an operating system for your containers that runs across multiple machines.
> - **What is AWS EC2?** Amazon Elastic Compute Cloud (EC2) provides virtual servers in the cloud. These are essentially computers you can rent by the hour/month to run your applications without having to buy physical hardware.
> - **Why use them together?** Combining EC2 with Kubernetes gives you a flexible, scalable infrastructure for running applications like MinIO in containers.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setting Up EC2 Instances](#setting-up-ec2-instances)
- [Installing Kubernetes](#installing-kubernetes)
- [Standalone MinIO Deployment](#standalone-minio-deployment)
- [Distributed MinIO Deployment](#distributed-minio-deployment)
- [Accessing MinIO](#accessing-minio)
- [Troubleshooting](#troubleshooting)
- [Cleanup](#cleanup)

## Prerequisites

Before you begin, ensure you have:

- An AWS account with permissions to create EC2 instances
  > If you're new to AWS, you'll need to sign up for an account at aws.amazon.com and set up billing. AWS offers a free tier for new users.

- AWS CLI installed and configured with appropriate credentials
  > The AWS Command Line Interface lets you control AWS services from your terminal. Install it from [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and run `aws configure` to set up your access keys.

- Basic understanding of Kubernetes concepts
  > Don't worry if you're new to Kubernetes! This guide will explain key concepts as we go. The official [Kubernetes Basics tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/) is also helpful.

- SSH client for connecting to EC2 instances
  > Windows users can use PuTTY or Windows Subsystem for Linux (WSL). Mac and Linux users have SSH built in.

## Setting Up EC2 Instances

> **Beginner's Note:** EC2 instances are virtual servers in the AWS cloud. You'll be creating one or more of these servers to run your Kubernetes cluster. Think of each instance as a separate computer that you're renting from AWS.

### For Standalone Deployment

1. **Launch an EC2 Instance**

   Launch an Ubuntu 22.04 LTS instance with at least:
   - t2.medium (2 vCPU, 4 GiB memory) or larger
     > This is the size of your virtual server. For Kubernetes, you need at least 2 CPUs and 4GB of RAM. Smaller instances won't work properly.
   - 20 GB of storage
     > This is the disk space for your server. 20GB is the minimum for running Kubernetes and MinIO.
   - Security group with the following ports open:
     > Security groups are like firewalls that control traffic to your instance.
     - 22 (SSH) - For remote access to your server
     - 6443 (Kubernetes API) - For Kubernetes control plane communication
     - 30000-32767 (NodePort range) - For accessing applications running on Kubernetes

   ```bash
   # This command creates a new EC2 instance
   # You'll need to replace several values with your own:
   # - your-key-pair: The name of your SSH key pair in AWS
   # - sg-xxxxxxxxxxxxxxxxx: Your security group ID
   
   aws ec2 run-instances \
     --image-id ami-0c7217cdde317cfec \  # Ubuntu 22.04 LTS (us-east-1)
     --instance-type t2.medium \
     --key-name your-key-pair \
     --security-group-ids sg-xxxxxxxxxxxxxxxxx \
     --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=k8s-master}]' \
     --count 1
   ```

   > **Alternative:** If you're not comfortable with the AWS CLI, you can also create instances through the AWS web console at https://console.aws.amazon.com/ec2/

### For Distributed Deployment

1. **Launch Multiple EC2 Instances**

   > **Beginner's Note:** A distributed deployment spreads your application across multiple servers for better reliability and performance. If one server fails, the others keep running.

   For a distributed setup, launch at least 4 instances:
   - 1 master node (t2.medium or larger)
     > The master node (also called control plane) manages the entire Kubernetes cluster
   - 3+ worker nodes (t2.medium or larger)
     > Worker nodes are where your applications actually run
   
   ```bash
   # Launch master node
   aws ec2 run-instances \
     --image-id ami-0c7217cdde317cfec \
     --instance-type t2.medium \
     --key-name your-key-pair \
     --security-group-ids sg-xxxxxxxxxxxxxxxxx \
     --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=k8s-master}]' \
     --count 1
     
   # Launch worker nodes
   aws ec2 run-instances \
     --image-id ami-0c7217cdde317cfec \
     --instance-type t2.medium \
     --key-name your-key-pair \
     --security-group-ids sg-xxxxxxxxxxxxxxxxx \
     --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=k8s-worker}]' \
     --count 3
   ```

2. **Connect to Your Instances**

   ```bash
   ssh -i /path/to/your-key-pair.pem ubuntu@your-instance-public-ip
   ```

## Installing Kubernetes

> **Beginner's Note:** Kubernetes installation has several components:
> - **Container runtime (containerd)**: Software that runs containers
> - **kubelet**: The primary agent that runs on each node
> - **kubeadm**: Tool to bootstrap the cluster
> - **kubectl**: Command-line tool to control Kubernetes
>
> The installation process is complex but you only need to do it once for your cluster.

### On All Nodes (Master and Workers)

1. **Update the System**

   ```bash
   # Always start with updated packages
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Container Runtime (containerd)**

   ```bash
   # Load required kernel modules for container networking
   # These modules allow containers to communicate with each other
   cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
   overlay
   br_netfilter
   EOF
   
   sudo modprobe overlay
   sudo modprobe br_netfilter
   
   # Set up required network parameters
   # These settings allow Kubernetes to properly manage container networking
   cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
   net.bridge.bridge-nf-call-iptables  = 1
   net.ipv4.ip_forward                 = 1
   net.bridge.bridge-nf-call-ip6tables = 1
   EOF
   
   sudo sysctl --system
   
   # Install containerd - the container runtime that will run your applications
   sudo apt install -y containerd
   
   # Configure containerd with default settings
   sudo mkdir -p /etc/containerd
   containerd config default | sudo tee /etc/containerd/config.toml
   
   # Update containerd to use systemd for cgroup management
   # This ensures proper resource allocation and management
   sudo sed -i 's/SystemdCgroup \= false/SystemdCgroup \= true/g' /etc/containerd/config.toml
   
   # Restart containerd to apply changes
   sudo systemctl restart containerd
   sudo systemctl enable containerd
   ```

3. **Install Kubernetes Components**

   ```bash
   # Add Kubernetes repository to get official packages
   sudo apt install -y apt-transport-https ca-certificates curl
   
   curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
   
   echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
   
   sudo apt update
   
   # Install the three main Kubernetes components:
   # - kubelet: the agent that runs on each node
   # - kubeadm: tool to create and manage clusters
   # - kubectl: command-line tool to control Kubernetes
   sudo apt install -y kubelet kubeadm kubectl
   
   # Pin their versions to prevent accidental upgrades
   # This ensures cluster stability
   sudo apt-mark hold kubelet kubeadm kubectl
   
   # Disable swap - Kubernetes requires swap to be turned off
   # This is a strict requirement for Kubernetes to function properly
   sudo swapoff -a
   sudo sed -i '/swap/d' /etc/fstab
   ```

### On Master Node Only

1. **Initialize the Kubernetes Cluster**

   ```bash
   # Get the public IP of your EC2 instance
   # This special URL works inside EC2 to get instance metadata
   MASTER_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
   
   # Initialize the Kubernetes cluster
   # --pod-network-cidr: Sets the IP address range for pods
   # --apiserver-advertise-address: Tells Kubernetes which IP to use for the API server
   sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --apiserver-advertise-address=$MASTER_IP
   
   # Set up kubectl configuration for the ubuntu user
   # This allows you to run kubectl commands without sudo
   mkdir -p $HOME/.kube
   sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
   sudo chown $(id -u):$(id -g) $HOME/.kube/config
   ```

2. **Install a Pod Network Add-on (Flannel)**

   ```bash
   # Install Flannel for pod networking
   # This creates a virtual network that allows pods to communicate across nodes
   kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
   ```

3. **Generate Join Command for Worker Nodes**

   ```bash
   # Create a token and print the command needed to join worker nodes
   kubeadm token create --print-join-command
   ```

   > **IMPORTANT:** Save the output command from this step. It will look something like:
   > `kubeadm join 192.168.1.100:6443 --token abcdef.0123456789abcdef --discovery-token-ca-cert-hash sha256:1234...`
   > You'll need this exact command to join worker nodes to your cluster.

### On Worker Nodes Only

1. **Join the Cluster**

   Run the join command you obtained from the master node:

   ```bash
   # Replace this with the actual command you got from the master node
   sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash <hash>
   ```

   > **Note:** This command must be run exactly as shown from the master node. The token is valid for 24 hours by default.

2. **Verify Nodes**

   On the master node, run:

   ```bash
   # Check the status of all nodes in the cluster
   kubectl get nodes
   ```

   All nodes should appear and eventually show as `Ready`. This may take a minute or two as the nodes initialize.
   
   > **Troubleshooting:** If nodes show `NotReady` status for more than a few minutes, check that the network plugin is properly installed on the master node.

## Standalone MinIO Deployment

> **Beginner's Note:** Now that your Kubernetes cluster is running, we'll deploy MinIO on it. MinIO is an object storage server compatible with Amazon S3. The standalone deployment runs a single instance of MinIO.

### Step 1: Create a Persistent Volume Claim (PVC)

1. **Create `minio-pvc.yaml`**

   ```bash
   # This creates a file with the PVC definition
   # A PVC (Persistent Volume Claim) requests storage space from the cluster
   cat <<EOF > minio-pvc.yaml
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
   EOF
   ```

   > **What this does:** This creates a request for 10GB of persistent storage. MinIO will use this to store data that persists even if the container restarts.

2. **Apply the PVC**

   ```bash
   # This submits the PVC request to Kubernetes
   kubectl apply -f minio-pvc.yaml
   ```

### Step 2: Create the MinIO Deployment

1. **Create `minio-deployment.yaml`**

   ```bash
   # This creates a file with the MinIO deployment definition
   cat <<EOF > minio-deployment.yaml
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
             - name: MINIO_ROOT_USER
               value: "minioadmin"
             - name: MINIO_ROOT_PASSWORD
               value: "minioadmin"
           ports:
             - containerPort: 9000  # API port
             - containerPort: 9090  # Console port
           volumeMounts:
             - name: minio-storage
               mountPath: /data
         volumes:
         - name: minio-storage
           persistentVolumeClaim:
             claimName: minio-pv-claim
   EOF
   ```

   > **What this does:** 
   > - Creates a deployment with 1 replica (1 instance) of MinIO
   > - Uses the official MinIO Docker image
   > - Sets up default login credentials (minioadmin/minioadmin)
   > - Mounts the persistent storage we requested earlier
   > - Exposes ports 9000 (API) and 9090 (Web Console)

2. **Apply the Deployment**

   ```bash
   # This creates the MinIO deployment in Kubernetes
   kubectl apply -f minio-deployment.yaml
   ```

### Step 3: Create a Service

1. **Create `minio-service.yaml`**

   ```bash
   # This creates a file with the service definition
   cat <<EOF > minio-service.yaml
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
   EOF
   ```

   > **What this does:** 
   > - Creates a service that exposes MinIO outside the cluster
   > - Uses NodePort type, which opens specific ports on all nodes
   > - Maps internal ports (9000, 9090) to external ports (30900, 30909)
   > - The selector connects this service to the MinIO deployment

2. **Apply the Service**

   ```bash
   # This creates the service in Kubernetes
   kubectl apply -f minio-service.yaml
   ```

## Distributed MinIO Deployment

> **Beginner's Note:** A distributed deployment runs multiple MinIO instances that work together as a single storage system. This provides better performance, capacity, and fault tolerance compared to a standalone deployment.

For a distributed setup, we'll use a StatefulSet to ensure stable network identities and persistent storage for each MinIO instance.

### Step 1: Create a Headless Service

1. **Create `minio-headless.yaml`**

   ```bash
   # This creates a file with the headless service definition
   cat <<EOF > minio-headless.yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: minio
   spec:
     clusterIP: None
     ports:
       - port: 9000
     selector:
       app: minio-distributed
   EOF
   ```

   > **What is a headless service?** A headless service doesn't have a cluster IP. Instead, it creates DNS entries for each pod, allowing them to find each other by name. This is essential for distributed MinIO, as each instance needs to know about the others.

2. **Apply the Headless Service**

   ```bash
   # This creates the headless service in Kubernetes
   kubectl apply -f minio-headless.yaml
   ```

### Step 2: Create the MinIO StatefulSet

1. **Create `minio-statefulset.yaml`**

   ```bash
   # This creates a file with the StatefulSet definition
   cat <<EOF > minio-statefulset.yaml
   apiVersion: apps/v1
   kind: StatefulSet
   metadata:
     name: minio
   spec:
     serviceName: minio
     replicas: 4
     selector:
       matchLabels:
         app: minio-distributed
     template:
       metadata:
         labels:
           app: minio-distributed
       spec:
         containers:
         - name: minio
           image: minio/minio:latest
           args:
           - server
           - --console-address
           - :9090
           - http://minio-{0...3}.minio.default.svc.cluster.local/data
           env:
           - name: MINIO_ROOT_USER
             value: "minioadmin"
           - name: MINIO_ROOT_PASSWORD
             value: "minioadmin"
           ports:
           - containerPort: 9000
           - containerPort: 9090
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
   EOF
   ```

   > **What is a StatefulSet?** Unlike a Deployment, a StatefulSet maintains a sticky identity for each pod. This is important for distributed applications where each instance needs a stable network identity and storage.
   >
   > **What this does:**
   > - Creates 4 MinIO instances (pods)
   > - Each pod gets a predictable name (minio-0, minio-1, etc.)
   > - Each pod gets its own persistent storage
   > - The pods can find each other using DNS names
   > - The `http://minio-{0...3}.minio.default.svc.cluster.local/data` argument tells MinIO to run in distributed mode

2. **Apply the StatefulSet**

   ```bash
   # This creates the StatefulSet in Kubernetes
   kubectl apply -f minio-statefulset.yaml
   ```

### Step 3: Create a Service for External Access

1. **Create `minio-distributed-service.yaml`**

   ```bash
   # This creates a file with the service definition for the distributed deployment
   cat <<EOF > minio-distributed-service.yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: minio-distributed-service
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
       app: minio-distributed
   EOF
   ```

   > **Note:** This service is similar to the one we created for the standalone deployment, but it targets pods with the `minio-distributed` label instead.

2. **Apply the Service**

   ```bash
   # This creates the service in Kubernetes
   kubectl apply -f minio-distributed-service.yaml
   ```

## Accessing MinIO

### For Standalone Deployment

1. **Get the EC2 Instance Public IP**

   ```bash
   INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
   echo "MinIO API: http://$INSTANCE_IP:30900"
   echo "MinIO Console: http://$INSTANCE_IP:30909"
   ```

2. **Access the MinIO Console**

   Open your browser and navigate to:
   ```
   http://<your-ec2-public-ip>:30909
   ```

3. **Log in with Default Credentials**

   - Username: minioadmin
   - Password: minioadmin

### For Distributed Deployment

Access is the same as for the standalone deployment, but you're now connecting to a distributed MinIO cluster.

> **Note:** When connecting to a distributed deployment, you're actually connecting to any one of the MinIO instances, but they work together as a single system. The distributed setup provides better performance and fault tolerance.

## Using MinIO with the MinIO Client (mc)

> **Beginner's Note:** The MinIO Client (mc) is a command-line tool that provides a modern alternative to UNIX commands like ls, cat, cp, mirror, diff, etc. for filesystems and object storage services like S3, Azure, GCS, and MinIO.

1. **Install the MinIO Client**

   ```bash
   # Download the MinIO Client binary
   wget https://dl.min.io/client/mc/release/linux-amd64/mc
   
   # Make it executable
   chmod +x mc
   
   # Move it to a directory in your PATH so you can run it from anywhere
   sudo mv mc /usr/local/bin/
   ```

2. **Configure the MinIO Client**

   ```bash
   INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
   mc alias set myminio http://$INSTANCE_IP:30900 minioadmin minioadmin
   ```

3. **Test the Connection**

   ```bash
   mc admin info myminio
   ```

4. **Basic Operations**

   ```bash
   # Create a bucket
   mc mb myminio/my-bucket
   
   # Upload a file
   echo "Hello MinIO" > test.txt
   mc cp test.txt myminio/my-bucket/
   
   # List objects in a bucket
   mc ls myminio/my-bucket/
   
   # Download a file
   mc cp myminio/my-bucket/test.txt ./downloaded.txt
   ```

## Troubleshooting

> **Beginner's Note:** When things don't work as expected, Kubernetes provides several commands to help you diagnose issues. These commands let you see the status of your resources and any error messages.

### Checking Pod Status

```bash
# List all pods and their status
kubectl get pods

# Get detailed information about a specific pod
kubectl describe pod <pod-name>

# View the logs (console output) from a pod
kubectl logs <pod-name>
```

### Checking Service Status

```bash
kubectl get services
kubectl describe service minio-service
```

### Common Issues

1. **Pods Stuck in Pending State**

   This often indicates insufficient resources or issues with PersistentVolumeClaims.
   
   ```bash
   kubectl describe pod <pod-name>
   ```

2. **Cannot Access MinIO**

   Check if the service is properly exposed:
   
   ```bash
   kubectl get svc
   ```
   
   Verify that the security group allows traffic on the NodePort range.

3. **Distributed Mode Issues**

   For distributed deployments, check that all pods are running:
   
   ```bash
   kubectl get pods -l app=minio-distributed
   ```

## Cleanup

> **Beginner's Note:** Cleanup is important to avoid ongoing charges for AWS resources you're no longer using. The cleanup process has multiple levels depending on what you want to remove.

### Standalone Deployment

```bash
# These commands remove just the MinIO application but leave Kubernetes running
kubectl delete service minio-service
kubectl delete deployment minio-deployment
kubectl delete pvc minio-pv-claim
```

### Distributed Deployment

```bash
# These commands remove just the distributed MinIO application
kubectl delete service minio-distributed-service
kubectl delete statefulset minio
kubectl delete service minio
kubectl delete pvc -l app=minio-distributed
```

### Uninstall Kubernetes (Optional)

> **Why uninstall Kubernetes?** If you're completely done with your testing and want to free up resources on your EC2 instances, you might want to uninstall Kubernetes. This is optional - you can leave Kubernetes installed if you plan to deploy other applications later.

On the master node:

```bash
# This prepares a node for removal by safely evicting all pods
kubectl drain <node-name> --delete-emptydir-data --force --ignore-daemonsets

# This removes the node from the cluster
kubectl delete node <node-name>
```

On each node:

```bash
# This resets the Kubernetes installation
sudo kubeadm reset

# This removes all Kubernetes packages
sudo apt-get purge kubeadm kubectl kubelet kubernetes-cni -y

# This removes any dependencies that are no longer needed
sudo apt-get autoremove -y

# This removes the kubectl configuration
sudo rm -rf ~/.kube
```

> **Note:** After uninstalling Kubernetes, you may want to terminate your EC2 instances if you no longer need them to avoid ongoing charges.

## Security Considerations

1. **Change Default Credentials**

   Always change the default MinIO credentials in production environments.

2. **Network Security**

   Restrict access to your Kubernetes cluster and MinIO services using AWS security groups.

3. **TLS Encryption**

   For production deployments, configure TLS for secure communication with MinIO.

4. **IAM Integration**

   Consider integrating with AWS IAM for more granular access control.

## Conclusion

You now have MinIO deployed on AWS EC2 using Kubernetes, either in standalone or distributed mode. This setup provides a scalable, Kubernetes-native object storage solution that's compatible with the S3 API.

For production environments, consider additional configurations such as:
- Setting up proper monitoring and alerting
- Implementing backup and disaster recovery strategies
- Configuring high availability across multiple availability zones
- Implementing proper security measures
