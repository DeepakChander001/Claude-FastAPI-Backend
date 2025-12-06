#!/bin/bash
set -e

# Helper functions for CI/CD pipelines

function run_tests() {
    echo "Installing dependencies..."
    pip install -r requirements.txt
    pip install pytest pytest-mock
    
    echo "Running tests..."
    export USE_MOCK_CLIENT=true
    pytest -q
}

function docker_build_verify() {
    echo "Verifying Docker build..."
    docker build -t test-build:latest .
    echo "Docker build successful."
}

function tf_plan() {
    echo "Running Terraform Plan..."
    cd infra/terraform
    terraform init
    terraform plan -out=plan.tfplan
    cd ../..
}
