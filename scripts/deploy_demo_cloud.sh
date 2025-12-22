#!/bin/bash
# @phylogenesis_signature(origin="OmniMind_DevOps", intent="deploy_frontend_ce")

echo "🚀 OMNIMIND DEMO DEPLOYMENT (CODE ENGINE NATIVE)"
echo "================================================"

# 1. Config
REGION="au-syd"
RESOURCE_GROUP="Default"
PROJECT_NAME="omnimind-demo"
BUILD_NAME="omnimind-build"
IMAGE_NAME="omnimind-glass-box"
APP_NAME="omnimind-glass-box"
ICR_NAMESPACE="omnimind-demo"
ICR_SERVER="au.icr.io"
IMAGE_URI="$ICR_SERVER/$ICR_NAMESPACE/$IMAGE_NAME:latest"

# 2. Config Target
echo "\n🎯 Targeting Region $REGION..."
ibmcloud target -r $REGION -g $RESOURCE_GROUP

# 3. Create Project
echo "\n🏗️  Ensuring Code Engine Project..."
if ! ibmcloud ce project list | grep -q "$PROJECT_NAME"; then
    ibmcloud ce project create --name $PROJECT_NAME
fi
ibmcloud ce project select --name $PROJECT_NAME

# 4. Configure Registry Access (Auto-managed by CE usually, but we need namespace)
echo "\n📦 Configuring Registry Namespace..."
ibmcloud cr login
if ! ibmcloud cr namespaces | grep -q "$ICR_NAMESPACE"; then
    ibmcloud cr namespace-add $ICR_NAMESPACE
fi

# 5. Define Build (Cloud Native Buildpacks or Dockerfile)
echo "\n🔨 Configuring Cloud Build..."
# We delete existing build to ensure fresh config if needed, or just update
if ibmcloud ce build get --name $BUILD_NAME &> /dev/null; then
    echo "   Build definition exists. Updating..."
    ibmcloud ce build update --name $BUILD_NAME \
        --image $IMAGE_URI \
        --source . \
        --dockerfile web/Dockerfile
else
    echo "   Creating build definition..."
    ibmcloud ce build create --name $BUILD_NAME \
        --image $IMAGE_URI \
        --source . \
        --dockerfile web/Dockerfile
fi

# 6. Submit Build Run (Uploads Local Source)
echo "\n🚀 Submitting Build Run (Uploading Source)..."
# capture the build run name
BUILD_RUN_NAME="build-run-$(date +%s)"
ibmcloud ce buildrun submit --build $BUILD_NAME --name $BUILD_RUN_NAME --wait

# Check Build Status
STATUS=$(ibmcloud ce buildrun get --name $BUILD_RUN_NAME --output json | grep "status" | head -n 1)
echo "   Build Status: $STATUS"

# 7. Deploy App
echo "\n🚀 Deploying App..."
# Env vars need to be passed securely.
# Ideally via Secrets, but for demo script we pass direct or create secret first.
# Let's create a secret for keys.
ibmcloud ce secret create --name omnimind-keys \
    --from-literal "IBM_CLOUD_API_KEY=$IBM_CLOUD_API_KEY" \
    --from-literal "IBM_CLOUD_SERVICE_KEY=$IBM_CLOUD_SERVICE_KEY" \
    --ignore-exist

ibmcloud ce app create --name $APP_NAME \
    --image $IMAGE_URI \
    --min-scale 1 \
    --max-scale 1 \
    --cpu 0.5 \
    --memory 1G \
    --port 8080 \
    --env-from-secret omnimind-keys

echo "\n✅ DEPLOYMENT COMPLETE!"
ibmcloud ce app get --name $APP_NAME --output url
