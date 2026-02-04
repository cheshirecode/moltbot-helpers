#!/bin/bash
# Secure credential management for moltbot-helpers
# This script provides a secure way to manage credentials without exposing them in shell config

# Function to securely load credentials when needed
load_credentials() {
    echo "Loading credentials securely..."
    
    # GitHub tokens (only if file exists and has proper permissions)
    if [ -f "$HOME/.github_token" ]; then
        # Check if file has secure permissions (owner read-only)
        perms=$(stat -c %a "$HOME/.github_token" 2>/dev/null)
        if [ "$perms" = "600" ] || [ "$perms" = "400" ]; then
            export GITHUB_TOKEN=$(cat "$HOME/.github_token")
            export GH_TOKEN=$(cat "$HOME/.github_token")
        else
            echo "WARNING: ~/.github_token has insecure permissions ($perms). Please set to 600."
        fi
    fi
    
    # Only load other credentials in secure environments if absolutely necessary
    # For development/testing only - should not be used in production
    if [ "$MOLTBOT_SECURE_ENV" = "true" ]; then
        if [ -f "$HOME/.secrets/supabase_keys" ]; then
            source "$HOME/.secrets/supabase_keys"
        fi
        
        if [ -f "$HOME/.secrets/llm_keys" ]; then
            source "$HOME/.secrets/llm_keys"
        fi
    fi
}

# Function to clear credentials from environment
clear_credentials() {
    unset GITHUB_TOKEN
    unset GH_TOKEN
    unset FAMILY_PLANNER_SUPABASE_SERVICE_ROLE_KEY
    unset VITE_FAMILY_PLANNER_SUPABASE_ANON_KEY
    unset VITE_FAMILY_PLANNER_SUPABASE_URL
    unset CLOUDFLARE_API_TOKEN_WORKERS
    unset OLLAMA_API_KEY
    unset DEEPSEEK_API_KEY
    unset ALIBABA_AI_API_KEY
    unset OPEN_ROUTER_API_KEY
    unset HF_TOKEN
    echo "Credentials cleared from environment"
}

# Function to check credential security
check_security() {
    echo "Checking credential security..."
    
    if [ -f "$HOME/.github_token" ]; then
        perms=$(stat -c %a "$HOME/.github_token" 2>/dev/null)
        if [ "$perms" != "600" ] && [ "$perms" != "400" ]; then
            echo "ERROR: ~/.github_token has insecure permissions ($perms). Should be 600 or 400."
            return 1
        fi
    fi
    
    # Check for exposed credentials in common shell files
    if grep -q "sk-" "$HOME/.shell_common" 2>/dev/null; then
        echo "WARNING: API keys detected in ~/.shell_common. These should be removed."
    fi
    
    if grep -q "sb_" "$HOME/.shell_common" 2>/dev/null; then
        echo "WARNING: Supabase keys detected in ~/.shell_common. These should be removed."
    fi
    
    echo "Security check completed"
    return 0
}

case "$1" in
    load)
        load_credentials
        ;;
    clear)
        clear_credentials
        ;;
    check)
        check_security
        ;;
    *)
        echo "Usage: $0 {load|clear|check}"
        exit 1
        ;;
esac