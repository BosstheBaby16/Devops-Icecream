# 🍦 IceCream App — DevOps Examination Project

A complete containerized Kubernetes deployment of the [IceCream](https://github.com/nored/IceCream) web application.

---

## 📁 Project Structure

```
icecream-devops/
├── Dockerfile                   # Multi-stage production Docker build
├── docker-compose.yaml          # Full local stack (app + nginx + redis)
├── nginx/
│   └── nginx.conf               # Reverse proxy config
├── k8s/
│   ├── deployment.yaml          # Kubernetes Deployment (3 replicas, probes, limits)
│   └── service.yaml             # Kubernetes NodePort Service
├── load-testing/
│   └── load_test.py             # Python async load tester (500 users / 60s)
├── scripts/
│   └── fault_simulation.py      # kubectl-based fault simulation & observability
└── README.md
```

---

## 🚀 Step-by-Step GitHub Setup

### Step 1 — Install Prerequisites

```bash
# Git
sudo apt install git         # Linux
brew install git              # macOS

# Docker Desktop: https://www.docker.com/products/docker-desktop
# Minikube:       https://minikube.sigs.k8s.io/docs/start/
# kubectl:        https://kubernetes.io/docs/tasks/tools/
```

---

### Step 2 — Create GitHub Repository

1. Go to [https://github.com/new](https://github.com/new)
2. Repository name: `icecream-devops`
3. Set to **Private** or **Public**
4. ✅ Add a README → Click **"Create repository"**

---

### Step 3 — Clone the IceCream App & Set Up Your Repo

```bash
# Clone the original IceCream app
git clone https://github.com/nored/IceCream.git
cd IceCream

# Initialize your own repo inside it
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/icecream-devops.git

# Copy DevOps files into this directory
# (Dockerfile, docker-compose.yaml, k8s/, load-testing/, scripts/, nginx/)
```

---

### Step 4 — Push All Files to GitHub

```bash
git add .
git commit -m "feat: initial DevOps setup - Dockerfile, k8s manifests, load test"
git branch -M main
git push -u origin main
```

---

## 🐳 Section 2: Containerization

### Build & Run with Docker

```bash
# Build image
docker build -t icecream-app:latest .

# Run standalone
docker run -p 3000:3000 icecream-app:latest

# Open browser: http://localhost:3000
```

### Run Full Stack with Docker Compose

```bash
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app

# Stop stack
docker-compose down
```

---

## ☸️ Section 3: Kubernetes on Minikube

### Start Minikube

```bash
minikube start --driver=docker --cpus=2 --memory=4g
```

### Load Image into Minikube

```bash
# Point Docker to Minikube's daemon
eval $(minikube docker-env)

# Build image directly inside Minikube
docker build -t icecream-app:latest .
```

### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Watch pods come up
kubectl get pods -w

# Check service
kubectl get service icecream-service
```

### Access the Application

```bash
# Get the Minikube URL
minikube service icecream-service --url

# OR get Minikube IP + NodePort
minikube ip        # e.g. 192.168.49.2
# Access at: http://192.168.49.2:30080
```

### Verify Pod Health

```bash
kubectl get pods -o wide
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

---

## 📊 Section 4: Load Testing

### Install Dependency

```bash
pip install aiohttp
```

### Run Load Test (500 users / 60 seconds)

```bash
# Replace IP with your Minikube IP
python load-testing/load_test.py \
  --url http://$(minikube ip):30080 \
  --users 500 \
  --duration 60
```

### Expected Output

```
=======================================================
       LOAD TEST RESULTS - IceCream App
=======================================================
  Duration          : 60.12 seconds
  Total Requests    : 3842
  Successful        : 3821
  Failed            : 21
  Success Rate      : 99.45%
  Requests/sec      : 63.91
-------------------------------------------------------
  Min Latency       : 8.21 ms
  Max Latency       : 412.33 ms
  Avg Latency       : 38.45 ms
  Median Latency    : 32.11 ms
  P95 Latency       : 89.22 ms
  P99 Latency       : 156.80 ms
=======================================================
```

### Monitor During Load Test (new terminal)

```bash
# Watch pod resource usage
kubectl top pods -l app=icecream --watch

# Watch pod status
kubectl get pods -l app=icecream -w
```

---

## 🔭 Section 5: Observability & Fault Tolerance

### Run Full Observability Report

```bash
python scripts/fault_simulation.py \
  --namespace default \
  --app icecream
```

### Manual kubectl Commands

```bash
# Pod logs
kubectl logs -l app=icecream --tail=100

# Describe all pods
kubectl describe pods -l app=icecream

# Watch restart count
kubectl get pods -l app=icecream -o wide --watch

# Simulate crash manually
kubectl delete pod <pod-name>
# Kubernetes auto-restarts it immediately
```

### Add Horizontal Pod Autoscaler (HPA)

```bash
kubectl autoscale deployment icecream-deployment \
  --cpu-percent=70 \
  --min=2 \
  --max=10

kubectl get hpa
```

---

## 📝 Commit Conventions

```bash
# After each major section, commit with descriptive messages:
git add .
git commit -m "feat: add Dockerfile and docker-compose setup"

git add k8s/
git commit -m "feat: add Kubernetes deployment and service manifests"

git add load-testing/
git commit -m "test: add async load testing script (500 users/60s)"

git add scripts/
git commit -m "ops: add fault simulation and observability script"

git push origin main
```

---

## 🛠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| Pods in `Pending` state | `kubectl describe pod <name>` → check Events |
| `ImagePullBackOff` | Set `imagePullPolicy: Never` in deployment.yaml for local Minikube |
| Service not accessible | `minikube service icecream-service` to get correct URL |
| Load test connection error | Verify Minikube IP: `minikube ip` |
| `top` command error | Enable metrics: `minikube addons enable metrics-server` |
