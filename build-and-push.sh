#!/bin/bash

# Build and Push Docker Image Script
# Usage: ./build-and-push.sh <your-dockerhub-username>

if [ -z "$1" ]; then
    echo "Error: Docker Hub username required"
    echo "Usage: ./build-and-push.sh <your-dockerhub-username>"
    exit 1
fi

USERNAME=$1
IMAGE_NAME="sculptor"
TAG="latest"

echo "🐳 Building Docker image..."
docker build -t $USERNAME/$IMAGE_NAME:$TAG .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "🚀 Pushing to Docker Hub..."
    docker push $USERNAME/$IMAGE_NAME:$TAG
    
    if [ $? -eq 0 ]; then
        echo "✅ Push successful!"
        echo ""
        echo "📦 Your image is now available at:"
        echo "   $USERNAME/$IMAGE_NAME:$TAG"
        echo ""
        echo "🚂 To deploy on Railway:"
        echo "   1. Go to railway.app"
        echo "   2. Create new project"
        echo "   3. Deploy from Docker image"
        echo "   4. Enter: $USERNAME/$IMAGE_NAME:$TAG"
        echo "   5. Add environment variables"
        echo ""
    else
        echo "❌ Push failed!"
        exit 1
    fi
else
    echo "❌ Build failed!"
    exit 1
fi
