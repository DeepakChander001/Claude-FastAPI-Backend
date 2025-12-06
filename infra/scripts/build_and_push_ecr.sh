#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="REPLACE_ME_ACCOUNT_ID"
REPO_NAME="claude-proxy"
IMAGE_TAG="latest"

echo "--------------------------------------------------"
echo "Building and Pushing Docker Image to ECR"
echo "Region: $AWS_REGION"
echo "Account: $AWS_ACCOUNT_ID"
echo "Repo: $REPO_NAME"
echo "--------------------------------------------------"

# 1. Login to ECR
echo "Logging in to ECR..."
# aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. Build Image
echo "Building Docker image..."
# docker build -t $REPO_NAME .

# 3. Tag Image
echo "Tagging image..."
# docker tag $REPO_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

# 4. Push Image
echo "Pushing to ECR..."
# docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

echo "--------------------------------------------------"
echo "Done! Image URI: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"
echo "Update your terraform.tfvars 'container_image' with this URI."
echo "--------------------------------------------------"
