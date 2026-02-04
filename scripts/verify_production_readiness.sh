#!/bin/bash
# verify_production_readiness.sh - Verify moltbot-helpers is ready for production

echo "🔍 Verifying moltbot-helpers production readiness..."

# Check that essential files exist
echo ""
echo "📋 Checking essential files..."

ESSENTIAL_FILES=(
    "Dockerfile.production"
    "pyproject.toml"
    "README.md"
    "PRODUCTION_DEPLOYMENT.md"
    "src/pt/cli.py"
    "src/fp/cli.py"
    "src/seek/cli.py"
    "src/integration/cli.py"
    "backup"
    "integrate"
    "lookup"
    "pt"
    "service-manager"
    "sync"
)

missing_files=()
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ ! -f "$file" ] && [ ! -d "$file" ]; then
        missing_files+=("$file")
        echo "❌ Missing: $file"
    else
        echo "✅ Found: $file"
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo ""
    echo "❌ CRITICAL: Missing ${#missing_files[@]} essential files. Cannot proceed."
    exit 1
fi

# Check that no development artifacts remain
echo ""
echo "🧹 Checking for development artifacts to avoid in production..."

DEV_ARTIFACTS=(
    "seek_env/"
    ".venv/lib/python3.12/site-packages"
    "*test*.py"
    "*.pyc"
    "__pycache__"
    "test_*"
)

found_artifacts=()
for artifact in "${DEV_ARTIFACTS[@]}"; do
    if [ "$artifact" = "*test*.py" ]; then
        test_files=$(find . -name "*test*.py" -not -path "./scripts/*" 2>/dev/null | head -5)
        if [ -n "$test_files" ]; then
            echo "⚠️  Found test files (may be OK): $test_files"
        fi
    elif [ "$artifact" = "*.pyc" ]; then
        pyc_files=$(find . -name "*.pyc" 2>/dev/null | head -5)
        if [ -n "$pyc_files" ]; then
            echo "⚠️  Found .pyc files (should be cleaned): $pyc_files"
        fi
    elif [ "$artifact" = "__pycache__" ]; then
        cache_dirs=$(find . -name "__pycache__" 2>/dev/null | head -5)
        if [ -n "$cache_dirs" ]; then
            echo "⚠️  Found __pycache__ directories (should be cleaned): $cache_dirs"
        fi
    elif [ "$artifact" = "test_*" ]; then
        test_scripts=$(find . -name "test_*" -maxdepth 1 2>/dev/null | head -5)
        if [ -n "$test_scripts" ]; then
            echo "⚠️  Found test scripts (should be cleaned): $test_scripts"
        fi
    elif [ -d "$artifact" ] || [ -f "$artifact" ]; then
        found_artifacts+=("$artifact")
        echo "❌ Found development artifact: $artifact"
    fi
done

# Check Dockerfile.production content
echo ""
echo "🔒 Checking Dockerfile.production security features..."

if grep -q "USER moltbot" Dockerfile.production; then
    echo "✅ Non-root user configured"
else
    echo "❌ Non-root user not configured in Dockerfile.production"
    found_artifacts+=("Dockerfile.security")
fi

if grep -q "PYTHONDONTWRITEBYTECODE=1" Dockerfile.production; then
    echo "✅ Python bytecode write disabled"
else
    echo "ℹ️  Python bytecode setting not found (not critical)"
fi

if grep -q "DEBIAN_FRONTEND=noninteractive" Dockerfile.production; then
    echo "✅ Non-interactive package installation"
else
    echo "ℹ️  Debian frontend setting not found (not critical)"
fi

# Check pyproject.toml for production readiness
echo ""
echo "📦 Checking pyproject.toml for production readiness..."

if grep -q "moltbot-helpers" pyproject.toml; then
    echo "✅ Project name correct"
else
    echo "❌ Project name incorrect in pyproject.toml"
    found_artifacts+=("pyproject.toml")
fi

if grep -q "pt = \"pt.cli:main\"" pyproject.toml; then
    echo "✅ CLI scripts properly defined"
else
    echo "❌ CLI scripts not properly defined in pyproject.toml"
    found_artifacts+=("pyproject.toml.scripts")
fi

# Check for sensitive information in source files
echo ""
echo "🔐 Checking for potentially sensitive information..."

SENSITIVE_PATTERNS=("sk-" "secret" "token" "password" "key" "credential")
found_sensitive=0
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    # Search for the pattern but exclude documentation and config files
    sensitive_found=$(find src/ -name "*.py" -exec grep -l "$pattern" {} \; 2>/dev/null | grep -v "__pycache__" | head -5)
    if [ -n "$sensitive_found" ]; then
        echo "⚠️  Found '$pattern' in source files (verify no hardcoded secrets): $sensitive_found"
        found_sensitive=1
    fi
done

if [ $found_sensitive -eq 0 ]; then
    echo "✅ No obvious sensitive patterns found in source code"
fi

# Summary
echo ""
echo "📋 Summary:"
echo "- Essential files: $((${#ESSENTIAL_FILES[@]} - ${#missing_files[@]})/${#ESSENTIAL_FILES[@]})"
echo "- Development artifacts: ${#found_artifacts[@]} issues found"
echo "- Security features: Checked"
echo ""

if [ ${#missing_files[@]} -eq 0 ] && [ ${#found_artifacts[@]} -eq 0 ]; then
    echo "🎉 SUCCESS: Repository appears ready for production deployment!"
    echo ""
    echo "Next steps:"
    echo "1. Build the production Docker image:"
    echo "   docker build -f Dockerfile.production -t moltbot-helpers:production ."
    echo "2. Review PRODUCTION_DEPLOYMENT.md for deployment instructions"
    echo "3. Test the image in a staging environment before production"
    exit 0
else
    echo "⚠️  RECOMMENDATION: Address the above issues before production deployment"
    exit 1
fi