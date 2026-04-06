#!/bin/bash
# install.sh - Greenlight Skills installer
# Usage:
#   curl -sSL .../install.sh | bash                    # Auto-detect platform
#   curl -sSL .../install.sh | bash -s -- --target cursor
#   curl -sSL .../install.sh | bash -s -- --target claude
#   curl -sSL .../install.sh | bash -s -- --target both

set -e

REPO_URL="https://github.com/K0hei27/fde-skills"
REPO_NAME="fde-skills"
TARGET=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --target)
            TARGET="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Install to a specific directory
install_to() {
    local base_dir="$1"
    local install_dir="$base_dir/skills/$REPO_NAME"
    
    mkdir -p "$base_dir/skills"
    
    if [ -d "$install_dir" ]; then
        echo "Updating $install_dir..."
        cd "$install_dir" && git pull
    else
        echo "Installing to $install_dir..."
        git clone "$REPO_URL" "$install_dir"
    fi
    
    echo "✓ Installed to $install_dir"
}

# Main logic
echo ""
echo "╔═══════════════════════════════════════╗"
echo "║   FDE Skills Installer                ║"
echo "╚═══════════════════════════════════════╝"
echo ""

case "$TARGET" in
    cursor)
        install_to "$HOME/.cursor"
        ;;
    claude)
        install_to "$HOME/.claude"
        ;;
    both)
        install_to "$HOME/.cursor"
        install_to "$HOME/.claude"
        ;;
    *)
        # Auto-detect
        if [ -d "$HOME/.cursor" ] && [ -d "$HOME/.claude" ]; then
            echo "Both Cursor and Claude Code detected. Installing to both..."
            install_to "$HOME/.cursor"
            install_to "$HOME/.claude"
        elif [ -d "$HOME/.cursor" ]; then
            install_to "$HOME/.cursor"
        elif [ -d "$HOME/.claude" ]; then
            install_to "$HOME/.claude"
        else
            echo "No IDE detected. Installing to Cursor location..."
            install_to "$HOME/.cursor"
        fi
        ;;
esac

echo ""
echo "Done! Restart your IDE to use the skills."
echo ""
echo "Available skills:"
echo "  • greenlight-testing  - Agentforce go-live readiness via Testing Center"
echo "  • agent-preview       - Quick testing via sf agent preview"
echo "  • lwc-dashboard       - LWC dashboard for test results"
echo ""
echo "To update later: cd ~/.cursor/skills/fde-skills && git pull"
