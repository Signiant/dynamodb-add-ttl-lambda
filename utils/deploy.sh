#!/bin/bash
set -e
deploy_env=$1

# TODO: Remove this pip install on next update
# Update the SAM cli version to latest - this is a workaround for a SAM cli issue
pip install --upgrade aws-sam-cli

# Replace <HOOK_URL> in samconfig.toml with value from HOOK_URL env var
sed -i "s|<HOOK_URL>|${HOOK_URL}|g" samconfig.toml

echo "Building"
sam build
echo "Deploying to ${deploy_env}"
sam deploy --config-env ${deploy_env} --no-fail-on-empty-changeset
