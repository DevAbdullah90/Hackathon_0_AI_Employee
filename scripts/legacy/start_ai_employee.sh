#!/bin/bash
# Start AI Employee Gold Tier Automation System (Unix/Linux/Mac)
# This script starts the complete workflow orchestrator

echo "============================================================"
echo "     AI Employee - Starting Gold Tier Automation System"
echo "============================================================"
echo ""

# Set Python path
PYTHON_PATH=${PYTHON_PATH:-python3}

# Set vault path (adjust if needed)
VAULT_PATH="${VAULT_PATH:-/path/to/AI_Employee_Vault}"

echo "Starting Workflow Orchestrator..."
echo "Vault: $VAULT_PATH"
echo ""

# Change to vault directory
cd "$VAULT_PATH" || exit 1

# Install required packages if needed
echo "Checking dependencies..."
$PYTHON_PATH -c "import schedule" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing schedule library..."
    $PYTHON_PATH -m pip install schedule
fi

$PYTHON_PATH -c "import watchdog" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing watchdog library..."
    $PYTHON_PATH -m pip install watchdog
fi

$PYTHON_PATH -c "import yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing pyyaml library..."
    $PYTHON_PATH -m pip install pyyaml
fi

echo ""
echo "============================================================"
echo "All dependencies checked. Starting main system..."
echo "============================================================"
echo ""
echo "The system will now:"
echo "  - Monitor the 'Approved' folder for files to process"
echo "  - Run periodic tasks (hourly, daily, weekly)"
echo "  - Check Reddit, Twitter, LinkedIn for opportunities"
echo "  - Generate content automatically"
echo "  - Create CEO briefings"
echo ""
echo "Press Ctrl+C to stop the system gracefully."
echo "============================================================"
echo ""

# Start the workflow orchestrator
$PYTHON_PATH workflow_orchestrator.py

echo ""
echo "============================================================"
echo "System stopped."
echo "============================================================"
echo ""
