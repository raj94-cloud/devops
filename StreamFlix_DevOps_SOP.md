# 🎬 StreamFlix on AWS — DevOps SOP Document
### Project: Deploy a Netflix-style Python App using AWS DevOps Tools
**Author:** DevOps Beginner Guide | **Region:** ap-south-1 (Mumbai)

---

## 📌 What We Built
A Netflix-style movie streaming app (StreamFlix) deployed on AWS using:
- **Python Flask** — Backend API + UI
- **Docker** — Containerization
- **Amazon ECR** — Docker image registry
- **Amazon ECS Fargate** — Run containers (no servers)
- **AWS CodePipeline + CodeBuild** — CI/CD automation
- **GitHub** — Source code repository

---

## 🏗️ Architecture Flow
```
Developer pushes code to GitHub
        ↓
CodePipeline triggers automatically
        ↓
CodeBuild builds Docker image
        ↓
Docker image pushed to ECR
        ↓
ECS Fargate pulls image & deploys
        ↓
App live on public IP :5000
```

---

## ⚙️ Prerequisites
| Tool | Purpose |
|------|---------|
| AWS Account | Cloud infrastructure |
| GitHub Account | Source code hosting |
| Git (Windows) | Push code from local |
| AWS CLI | Manage AWS from terminal |
| Docker | Build container images |

---

## 📁 Project File Structure
```
streamflix/
├── app.py              ← Flask application
├── requirements.txt    ← Python dependencies
├── Dockerfile          ← Container build instructions
├── buildspec.yml       ← CodeBuild instructions
└── templates/
    └── index.html      ← Netflix-style UI
```

---

## 🔐 STEP 1 — Configure AWS CLI
> **Purpose:** Connect your terminal to your AWS account

### Console:
1. Go to **IAM → Users → Your User → Security Credentials**
2. Click **Create Access Key**
3. Copy **Access Key ID** and **Secret Access Key**

### Script (PowerShell/Terminal):
```bash
aws configure set aws_access_key_id YOUR_ACCESS_KEY
aws configure set aws_secret_access_key YOUR_SECRET_KEY
aws configure set region ap-south-1
aws configure set output json
```

### Verify:
```bash
aws sts get-caller-identity
```
✅ **Expected:** Returns your AWS Account ID and User ARN

---

## 🖥️ STEP 2 — Launch EC2 Instance (Build Server)
> **Purpose:** A Linux server to build and test your app

### Console:
1. Go to **EC2 → Instances → Launch Instance**
2. Name: `devops project-1`
3. AMI: **Ubuntu 22.04 LTS**
4. Instance Type: **t2.micro** (Free Tier ✅)
5. Key Pair: Create new → name `devops` → Download `.pem` file
6. Security Group: Allow **SSH (port 22)**
7. Click **Launch Instance**

### Script (AWS CLI):
```bash
aws ec2 run-instances \
  --image-id ami-07f919f92632ae971 \
  --instance-type t2.micro \
  --key-name devops \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=devops project-1}]' \
  --region ap-south-1
```

### Connect via SSH (Windows PowerShell):
```powershell
# Fix key permissions
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls D:\devops.pem /reset
icacls D:\devops.pem /inheritance:r
icacls D:\devops.pem /grant:r "${user}:(R)"

# Connect
ssh -i D:\devops.pem ubuntu@<PUBLIC_IP>
```

⚠️ **Key Points:**
- Save `.pem` file immediately — it cannot be downloaded again
- t2.micro = 1 vCPU, 1GB RAM — Free Tier eligible
- Public IP changes every time instance restarts

---

## 📦 STEP 3 — Create Application Files
> **Purpose:** Build the StreamFlix Python app

### app.py (Flask Application):
```python
from flask import Flask, jsonify, render_template
app = Flask(__name__)

movies = [
    {"id": 1, "title": "Inception", "genre": "Sci-Fi", "rating": 8.8,
     "trailer": "https://www.youtube.com/embed/YoHD9XEInc0"},
    {"id": 2, "title": "The Dark Knight", "genre": "Action", "rating": 9.0,
     "trailer": "https://www.youtube.com/embed/EXeTwQWrcwY"},
]

@app.route("/")
def home():
    return render_template("index.html", movies=movies)

@app.route("/movies")
def get_movies():
    return jsonify(movies)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

### requirements.txt:
```
flask==3.0.0
gunicorn==21.2.0
```

### Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

### buildspec.yml (CodeBuild instructions):
```yaml
version: "0.2"
phases:
  pre_build:
    commands:
      - aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 596652342676.dkr.ecr.ap-south-1.amazonaws.com
  build:
    commands:
      - docker build -t streamflix:latest .
      - docker tag streamflix:latest 596652342676.dkr.ecr.ap-south-1.amazonaws.com/streamflix:latest
      - docker push 596652342676.dkr.ecr.ap-south-1.amazonaws.com/streamflix:latest
```

---

## 🐙 STEP 4 — Push Code to GitHub
> **Purpose:** Store code in GitHub so CodePipeline can access it

### Script (PowerShell):
```powershell
cd D:\streamflix
git init
git add .
git commit -m "Initial StreamFlix app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

⚠️ **Key Points:**
- Use **Personal Access Token** as password (not GitHub password)
- Create token: GitHub → Settings → Developer Settings → Personal Access Tokens → repo scope
- If push rejected: `git push -u origin main --force`

---

## 🗄️ STEP 5 — Create ECR Repository
> **Purpose:** Store Docker images on AWS

### Console:
1. Go to **ECR → Repositories → Create Repository**
2. Name: `streamflix`
3. Click **Create**

### Script (AWS CLI):
```bash
aws ecr create-repository \
  --repository-name streamflix \
  --region ap-south-1
```

✅ **Your ECR URI:**
```
596652342676.dkr.ecr.ap-south-1.amazonaws.com/streamflix
```

---

## 🚀 STEP 6 — Create CodePipeline (CI/CD)
> **Purpose:** Automatically build and deploy on every code push

### Console:
1. Go to **CodePipeline → Create Pipeline**
2. Select **"Push to ECR"** template
3. Fill details:
   - **ConnectionArn:** Connect to GitHub
   - **FullRepositoryId:** `username/repo-name`
   - **BranchName:** `main`
   - **CodePipelineName:** `StreamFlix-Pipeline`
   - **DockerFilePath:** `./Dockerfile`
   - **ImageTag:** `latest`
4. Click **Create Pipeline**

⚠️ **Common Fixes Applied:**
```bash
# Fix 1: Enable Docker (Privileged Mode) in CodeBuild
aws codebuild update-project \
  --name YOUR_PROJECT \
  --environment privilegedMode=true,type=LINUX_CONTAINER,\
image=aws/codebuild/standard:7.0,computeType=BUILD_GENERAL1_SMALL

# Fix 2: Add ECR push permissions to CodeBuild IAM role
# IAM → Roles → CodeBuildRole → Add inline policy:
{
  "Effect": "Allow",
  "Action": [
    "ecr:GetAuthorizationToken",
    "ecr:BatchCheckLayerAvailability",
    "ecr:InitiateLayerUpload",
    "ecr:UploadLayerPart",
    "ecr:CompleteLayerUpload",
    "ecr:PutImage"
  ],
  "Resource": "*"
}
```

---

## 🐳 STEP 7 — Create ECS Cluster
> **Purpose:** The environment where your container runs

### Console:
1. Go to **ECS → Clusters → Create Cluster**
2. Name: `streamflix-cluster`
3. Infrastructure: **AWS Fargate** (serverless ✅)
4. Click **Create**

### Script (AWS CLI):
```bash
aws ecs create-cluster \
  --cluster-name streamflix-cluster \
  --region ap-south-1
```

---

## 📋 STEP 8 — Create ECS Task Definition
> **Purpose:** Define how your container should run

### Console:
1. Go to **ECS → Task Definitions → Create**
2. Family: `streamflix-task`
3. Launch type: **Fargate**
4. CPU: `0.25 vCPU` | Memory: `0.5 GB`
5. Container:
   - Name: `streamflix`
   - Image URI: `596652342676.dkr.ecr.ap-south-1.amazonaws.com/streamflix:latest`
   - Port: `5000`
6. Click **Create**

---

## 🌐 STEP 9 — Create ECS Service
> **Purpose:** Keep your container running 24/7

### Console:
1. Go to **ECS → streamflix-cluster → Services → Create**
2. Launch type: **Fargate**
3. Task Definition: `streamflix-task`
4. Service Name: `streamflix-service`
5. Desired Tasks: `1`
6. Networking: Select VPC + Subnet → **Enable Public IP** ✅
7. Click **Create**

⚠️ **Force New Deployment** (after each pipeline run):
1. ECS → streamflix-cluster → Services
2. Click streamflix-service → **Update Service**
3. Check ✅ **Force new deployment**
4. Click **Update**

---

## 🔍 STEP 10 — Get Public IP & Test
> **Purpose:** Access your live application

### Console:
1. **ECS → streamflix-cluster → Tasks tab**
2. Click running Task ID
3. Scroll to **Network** → Copy **Public IP**

### Test Endpoints:
```
http://<PUBLIC_IP>:5000          ← Netflix UI with movie posters
http://<PUBLIC_IP>:5000/movies   ← JSON API - all movies
http://<PUBLIC_IP>:5000/movies/1 ← Single movie
http://<PUBLIC_IP>:5000/movies/search?q=dark ← Search
```

---

## 🔄 CI/CD Flow — How Updates Work
```
1. Edit code locally (D:\streamflix\)
2. git add . && git commit -m "update" && git push origin main
3. CodePipeline auto-triggers ✅
4. CodeBuild builds new Docker image ✅
5. Image pushed to ECR ✅
6. Go to ECS → Update Service → Force new deployment ✅
7. New version live! ✅
```

---

## 💰 Cost Summary (Mumbai Region)
| Service | Cost |
|---------|------|
| EC2 t2.micro | Free (750 hrs/month, 12 months) |
| ECR | $0.10/GB/month storage |
| ECS Fargate (0.25 vCPU, 0.5GB) | ~$0.01/hour (~$7/month) |
| CodeBuild | 100 min/month free |
| CodePipeline | 1 pipeline free/month |

---

## 🛠️ Troubleshooting Quick Reference
| Error | Fix |
|-------|-----|
| `Permission denied (publickey)` | Fix .pem permissions with icacls |
| `docker build: no such file` | Ensure Dockerfile is in repo root |
| `AccessDeniedException: codebuild:StartBuild` | Add StartBuild permission to CodePipeline IAM role |
| `docker push: denied` | Add ECR permissions to CodeBuild IAM role |
| `docker build failed` | Enable Privileged Mode in CodeBuild |
| App shows old version | Force new deployment in ECS service |

---

## 🚀 Next Steps (Advanced)
- [ ] **ALB** — Add Load Balancer for port 80 (no :5000 in URL)
- [ ] **Route53** — Custom domain (e.g., streamflix.com)
- [ ] **ACM** — Free HTTPS/SSL certificate
- [ ] **RDS** — Replace in-memory data with PostgreSQL database
- [ ] **Auto Scaling** — Scale ECS tasks based on traffic
- [ ] **CloudWatch** — Monitoring and alerts
- [ ] **EKS** — Migrate to Kubernetes (needs t3.medium+)

---

*Document generated: April 2026 | AWS Region: ap-south-1 (Mumbai)*
