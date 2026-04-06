#!/bin/bash
# Connect to Salesforce CLI
# Helper script to authenticate to a Salesforce org

set -e

if [ -z "$1" ]; then
    echo "Usage: ./connect_sf_cli.sh <alias>"
    echo "Example: ./connect_sf_cli.sh my-org"
    echo ""
    echo "This will open a browser for Salesforce login."
    exit 1
fi

ALIAS="$1"

echo "Connecting to Salesforce..."
echo "Alias: $ALIAS"
echo ""
echo "A browser window will open for authentication."
echo ""

sf org login web --alias "$ALIAS"

echo ""
echo "Verifying connection..."
sf org display --target-org "$ALIAS"

echo ""
echo "Connected to $ALIAS"
