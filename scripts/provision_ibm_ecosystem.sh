#!/bin/bash
# 🚀 OmniMind IBM Ecosystem Provisioner
# Triggered by: Gemini Antigravity
# Goal: Provision 'Lite' (Free) services to generate integration data.

echo "🔮 Initializing IBM Cloud Ecosystem..."

# 1. Cloud Object Storage (The Cortex Backup)
echo "📦 Provisioning Cloud Object Storage (Lite)..."
ibmcloud resource service-instance-create omnimind-cortex-cos cloud-object-storage lite global

# 2. Cloudant NoSQL (The Narrative Ledger)
echo "🗄️  Provisioning Cloudant DB (Lite)..."
# Cloudant requires a region (using au-syd as configured, or us-south if lite not available there)
# Trying current region first
ibmcloud resource service-instance-create omnimind-ledger-db cloudantnosqldb lite au-syd || \
ibmcloud resource service-instance-create omnimind-ledger-db cloudantnosqldb lite us-south

# 3. Watson Machine Learning (The Somatic Effector)
echo "🧠 Provisioning Watson Machine Learning (Lite)..."
ibmcloud resource service-instance-create omnimind-wml pm-20 lite au-syd || \
ibmcloud resource service-instance-create omnimind-wml pm-20 lite us-south

# 4. Verify
echo "✅ Verifying Resources..."
ibmcloud resource service-instances

echo "🎉 Deployment Complete. OmniMind now has a cloud body."
