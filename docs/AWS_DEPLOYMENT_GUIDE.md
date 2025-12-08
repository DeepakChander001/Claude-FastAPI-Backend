# AWS Deployment Guide - Claude Proxy API

> **Prerequisite**: You already have an AWS IAM user with login credentials (email/password) provided by your organization.

---

## Table of Contents
1. [Login to AWS Console](#step-1-login-to-aws-console)
2. [Install AWS CLI on Your Computer](#step-2-install-aws-cli-on-your-computer)
3. [Get Your Access Keys from AWS](#step-3-get-your-access-keys-from-aws)
4. [Configure AWS CLI](#step-4-configure-aws-cli)
5. [Create EC2 Instance](#step-5-create-ec2-instance)
6. [Connect to Your EC2 Instance](#step-6-connect-to-your-ec2-instance)
7. [Deploy the Application](#step-7-deploy-the-application)
8. [Run as Background Service](#step-8-run-as-background-service)
9. [Test Your Deployed API](#step-9-test-your-deployed-api)

---

## Step 1: Login to AWS Console

1. Open your browser and go to: **https://console.aws.amazon.com/**
2. Enter your **IAM user credentials** (provided by your organization):
   - Account ID or alias (if required)
   - IAM username
   - Password
3. Click **Sign in**

You should now see the AWS Management Console.

---

## Step 2: Install AWS CLI on Your Computer

### Windows Installation

1. Download AWS CLI installer: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Run the downloaded `.msi` file
3. Click **Next** → **Next** → **Install** → **Finish**
4. **Close and reopen** your terminal (Git Bash or PowerShell)
5. Verify installation:
```bash
aws --version
```
You should see: `aws-cli/2.x.x Python/3.x.x Windows/10`

---

## Step 3: Get Your Access Keys from AWS

> **Note**: If you don't have permission to create access keys, ask your senior to provide them to you.

### If You Can Create Access Keys:

1. In AWS Console, click your **username** in the top-right corner
2. Click **Security credentials**
3. Scroll down to **Access keys**
4. Click **Create access key**
5. Select **Command Line Interface (CLI)**
6. Check the confirmation box
7. Click **Create access key**
8. **⚠️ IMPORTANT: Copy and save both keys NOW!**

```
┌─────────────────────────────────────────────────────┐
│ Access Key ID:     AKIA......................       │
│ Secret Access Key: wJalrXUt....................     │
└─────────────────────────────────────────────────────┘
```

### If Your Senior Provides Access Keys:

Your senior will give you two values:
- **Access Key ID** (starts with `AKIA...`)
- **Secret Access Key** (long random string)

Save these securely.

---

## Step 4: Configure AWS CLI

Open your terminal (Git Bash or PowerShell) and run:

```bash
aws configure
```

Enter the values when prompted:

```
AWS Access Key ID [None]: PASTE_YOUR_ACCESS_KEY_ID_HERE
AWS Secret Access Key [None]: PASTE_YOUR_SECRET_KEY_HERE
Default region name [None]: ap-south-1
Default output format [None]: json
```

**Choose a region closest to your users:**
| Location | Region Code |
|----------|-------------|
| Mumbai, India | `ap-south-1` |
| Singapore | `ap-southeast-1` |
| US East (Virginia) | `us-east-1` |
| Europe (Frankfurt) | `eu-central-1` |

### Verify Configuration:
```bash
aws sts get-caller-identity
```

If successful, you'll see your account information.

---

## Step 5: Create EC2 Instance

### 5.1 Go to EC2 Dashboard

1. In AWS Console, type **"EC2"** in the search bar
2. Click **EC2** from the results
3. Click the orange button **"Launch instance"**

### 5.2 Configure Your Instance

**Name and tags:**
```
Name: claude-proxy-server
```

**Application and OS Images (AMI):**
- Click **Ubuntu**
- Select: **Ubuntu Server 22.04 LTS (HVM), SSD Volume Type**
- Architecture: **64-bit (x86)**

**Instance type:**
- Select: **t2.micro** (Free tier eligible)
- Or **t2.small** for better performance

**Key pair (login):**
1. Click **"Create new key pair"**
2. Key pair name: `claude-proxy-key`
3. Key pair type: **RSA**
4. Private key file format: **.pem**
5. Click **"Create key pair"**
6. **⚠️ A file `claude-proxy-key.pem` will download - SAVE IT!**

**Network settings:**
Click **"Edit"** and configure:
- ✅ Allow SSH traffic from: **Anywhere** (0.0.0.0/0)
- ✅ Allow HTTPS traffic from the internet
- ✅ Allow HTTP traffic from the internet

**Add custom rule for API port:**
1. Click **"Add security group rule"**
2. Type: **Custom TCP**
3. Port range: **8000**
4. Source type: **Anywhere**
5. Source: **0.0.0.0/0**

**Configure storage:**
- Keep default: **8 GiB gp3**

### 5.3 Launch Instance

1. Click **"Launch instance"**
2. Wait for success message
3. Click **"View all instances"**
4. Wait until **Instance state** shows **"Running"** (green)

### 5.4 Get Your Instance IP Address

1. Click on your instance name `claude-proxy-server`
2. In the details panel, find **"Public IPv4 address"**
3. Copy this IP address (example: `13.234.56.78`)
4. **📝 Save this IP - you'll need it!**

---

## Step 6: Connect to Your EC2 Instance

### 6.1 Move Your Key File

Open Git Bash and run:

```bash
# Create .ssh folder if it doesn't exist
mkdir -p ~/.ssh

# Move your downloaded key file
mv ~/Downloads/claude-proxy-key.pem ~/.ssh/

# Set correct permissions (REQUIRED)
chmod 400 ~/.ssh/claude-proxy-key.pem
```

### 6.2 Connect via SSH

```bash
ssh -i ~/.ssh/claude-proxy-key.pem ubuntu@YOUR_EC2_IP_ADDRESS
```

**Example:**
```bash
ssh -i ~/.ssh/claude-proxy-key.pem ubuntu@13.234.56.78
```

When asked "Are you sure you want to continue connecting?" type: **yes**

**🎉 You are now connected to your AWS server!**

You should see:
```
ubuntu@ip-172-31-xx-xx:~$
```

---

## Step 7: Deploy the Application

Run these commands on your EC2 instance (after SSH connection):

### 7.1 Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 7.2 Install Required Software

```bash
sudo apt install -y python3 python3-pip python3-venv git
```

### 7.3 Clone Your Repository from GitHub

Since your code is already pushed to GitHub, clone it directly:

```bash
cd ~
git clone https://github.com/DeepakChander001/Claude-FastAPI-Backend.git EC2-Backend
cd EC2-Backend
```

**Verify the files are there:**
```bash
ls -la
```

You should see files like `requirements.txt`, `src/`, `docs/`, etc.

### 7.4 Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 7.5 Create Environment File

```bash
nano .env
```

Paste this content (replace with YOUR values):

```env
# Environment
ENVIRONMENT=production

# Anthropic API (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE
USE_MOCK_CLIENT=false
DEFAULT_MODEL=claude-3-haiku-20240307

# Supabase (if you use it)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key

# Security
AUTH_MODE=none
```

**Save the file:**
- Press `Ctrl + O` (save)
- Press `Enter` (confirm filename)
- Press `Ctrl + X` (exit)

### 7.6 Test the Application

```bash
source venv/bin/activate
uvicorn src.app.main:app --host 0.0.0.0 --port 8000
```

**Test in your browser:**
```
http://YOUR_EC2_IP:8000/health
```

You should see: `{"status":"ok"}`

Press `Ctrl + C` to stop the test server.

---

## Step 8: Run as Background Service

This makes your API run automatically even after you disconnect.

### 8.1 Create Service File

```bash
sudo nano /etc/systemd/system/claude-proxy.service
```

Paste this content:

```ini
[Unit]
Description=Claude Proxy API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/EC2-Backend
Environment="PATH=/home/ubuntu/EC2-Backend/venv/bin"
EnvironmentFile=/home/ubuntu/EC2-Backend/.env
ExecStart=/home/ubuntu/EC2-Backend/venv/bin/uvicorn src.app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl + O`, Enter, `Ctrl + X`

### 8.2 Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable claude-proxy
sudo systemctl start claude-proxy
```

### 8.3 Check Status

```bash
sudo systemctl status claude-proxy
```

You should see: **Active: active (running)**

### Useful Commands:

```bash
# View logs
sudo journalctl -u claude-proxy -f

# Restart service
sudo systemctl restart claude-proxy

# Stop service
sudo systemctl stop claude-proxy
```

---

## Step 9: Test Your Deployed API

### Browser Test

Open in your browser:
```
http://YOUR_EC2_IP:8000/health
```

### Postman Test

| Field | Value |
|-------|-------|
| Method | `POST` |
| URL | `http://YOUR_EC2_IP:8000/api/generate` |

**Headers:**
| Key | Value |
|-----|-------|
| Content-Type | application/json |

**Body (raw JSON):**
```json
{
    "prompt": "What is artificial intelligence? Explain simply.",
    "max_tokens": 500
}
```

**Expected Response:**
```json
{
    "request_id": "msg_01ABC...",
    "output": "Artificial intelligence (AI) is...",
    "model": "claude-3-haiku-20240307",
    "usage": {...}
}
```

---

## Summary: Information You Collected

| Item | Your Value |
|------|------------|
| AWS Access Key ID | `AKIA...` |
| AWS Secret Access Key | `...` |
| Region | `ap-south-1` |
| EC2 Public IP | `x.x.x.x` |
| Key Pair File | `~/.ssh/claude-proxy-key.pem` |
| Anthropic API Key | `sk-ant-...` |

---

## Troubleshooting

### "Permission denied" when connecting via SSH
```bash
chmod 400 ~/.ssh/claude-proxy-key.pem
```

### Cannot access port 8000 from browser
- Go to EC2 → Security Groups → Your security group
- Add inbound rule: Custom TCP, Port 8000, Source 0.0.0.0/0

### Service not starting
```bash
sudo journalctl -u claude-proxy -n 50
```
This shows the last 50 log lines to help debug.

### API returning 500 error
- Check your `.env` file has correct `ANTHROPIC_API_KEY`
- Verify `USE_MOCK_CLIENT=false`

---

## Your API Endpoint

After deployment, your API is available at:

```
http://YOUR_EC2_IP:8000/api/generate
```

Share this URL with anyone who needs to use your Claude Proxy API! 🚀
