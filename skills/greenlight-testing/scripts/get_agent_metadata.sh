#!/bin/bash
# Get Agent Metadata
# Retrieves Bot and GenAiPlannerBundle metadata from a Salesforce org

set -e

if [ -z "$1" ]; then
    echo "Usage: ./get_agent_metadata.sh <org_alias>"
    echo "Example: ./get_agent_metadata.sh my-org"
    exit 1
fi

ORG_ALIAS="$1"

echo "Retrieving agent metadata from: $ORG_ALIAS"
echo ""

# Retrieve Bot metadata
echo "Retrieving Bot metadata..."
sf project retrieve start --metadata "Bot:*" --target-org "$ORG_ALIAS" || {
    echo "Warning: Could not retrieve Bot metadata"
}

echo ""

# Retrieve GenAiPlannerBundle metadata (contains topics and actions)
echo "Retrieving GenAiPlannerBundle metadata..."
sf project retrieve start --metadata "GenAiPlannerBundle:*" --target-org "$ORG_ALIAS" || {
    echo "Warning: Could not retrieve GenAiPlannerBundle metadata"
}

echo ""
echo "Done! Check force-app/main/default/ for retrieved metadata."
echo ""
echo "To extract and view metadata:"
echo "  python scripts/extract_agent_metadata.py"
