#!/bin/bash
set -e

APP_NAME=${1:-"personal-website"}
NAMESPACE=${2:-"argocd"}

echo "Verifying sync status for ArgoCD application: $APP_NAME in namespace: $NAMESPACE"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed"
    exit 1
fi

# Get Application status
# We capture output and error. If it fails, kubectl usually prints to stderr.
if ! APP_JSON=$(kubectl get application "$APP_NAME" -n "$NAMESPACE" -o json 2>/dev/null); then
    echo "Error: Failed to get application '$APP_NAME' in namespace '$NAMESPACE'. It may not exist or you may not have access."
    exit 1
fi

# Parse JSON using python3 for reliability (avoids dependency on jq)
STATUS_CHECK=$(echo "$APP_JSON" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    sync = data.get('status', {}).get('sync', {}).get('status', 'Unknown')
    health = data.get('status', {}).get('health', {}).get('status', 'Unknown')
    print(f'{sync}|{health}')
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
")

SYNC_STATE=$(echo "$STATUS_CHECK" | cut -d'|' -f1)
HEALTH_STATE=$(echo "$STATUS_CHECK" | cut -d'|' -f2)

echo "Sync Status: $SYNC_STATE"
echo "Health Status: $HEALTH_STATE"

if [ "$SYNC_STATE" == "Synced" ] && [ "$HEALTH_STATE" == "Healthy" ]; then
    echo "✅ Application is Synced and Healthy."
    exit 0
else
    echo "❌ Application is NOT in desired state."
    exit 1
fi
