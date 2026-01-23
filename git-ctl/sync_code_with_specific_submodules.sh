#!/bin/bash

# ==============================================================================
# Script Name: sync_code.sh
# Description: Synchronizes the root project and specific submodules.
#              Renames the local directory to 'My_local_dir' and performs selective 
#              syncing to optimize performance in the Jenkins workspace.
# ==============================================================================

# --- Configuration ---
# The base path for development or execution 
WORKSPACE="/opt/path/to/robotframework/execution/root/"

# The target folder name (Case-sensitive as per requirement)
PROJECT_DIR="My_project_dir"

# Root project SSH URL
REMOTE_URL="ssh://git@://git-server"

# List only the submodules required for the build to save time/bandwidth
# Names must match the paths defined in the .gitmodules file
SUBMODULES=("submodule-1" "submodule-2")

# --- Execution ---

# 1. Change directory to the Jenkins workspace
cd "$WORKSPACE" || { echo "Error: Cannot access $WORKSPACE"; exit 1; }

# 2. Check if the project folder exists to determine if we Clone or Pull
if [ ! -d "$PROJECT_DIR" ]; then
    echo "[INFO] First-time sync: Cloning root project into '$PROJECT_DIR'..."
    
    # Clone the repository and force the local folder name to 'Rwbot'
    git clone "$REMOTE_URL" "$PROJECT_DIR"
    
    cd "$PROJECT_DIR" || exit 1
    
    # Initialize and download ONLY the specified submodules
    echo "[INFO] Initializing selected submodules: ${SUBMODULES[*]}..."
    git submodule update --init -- "${SUBMODULES[@]}"
else
    echo "[INFO] Daily sync: Updating existing '$PROJECT_DIR' directory..."
    cd "$PROJECT_DIR" || exit 1
    
    # Refresh remote tracking information
    git fetch --all
    
    # Pull latest changes from the main branch. 
    # Tries 'main' first, falls back to 'master' if main doesn't exist.
    echo "[INFO] Pulling latest changes for root project..."
    git pull origin main || git pull origin master
    
    # Sync selected submodules to their latest remote versions
    # --remote: Fetch the latest commit from the submodule's own origin
    # --merge: Merge the remote changes into your local submodule branch
    echo "[INFO] Updating selected submodules..."
    git submodule update --remote --merge -- "${SUBMODULES[@]}"
fi

echo "[SUCCESS] Sync completed for $PROJECT_DIR and submodules: ${SUBMODULES[*]}."
