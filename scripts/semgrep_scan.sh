#!/bin/bash
# Semgrep SAST Scan Script
# This script runs Semgrep security scanning on the Django project
# Usage: ./scripts/semgrep_scan.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Semgrep SAST Scan ===${NC}"
echo ""

# Check if Semgrep is installed
if ! command -v semgrep &> /dev/null; then
    echo -e "${RED}Error: Semgrep is not installed.${NC}"
    echo "Install it with: pipx install semgrep"
    echo "Or: pip install semgrep"
    exit 1
fi

# Get the project root directory (parent of scripts directory)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"
echo "Using rulesets: OWASP Top 10, Security Audit, Python, Django"
echo ""

# Run Semgrep scan
echo -e "${YELLOW}Running Semgrep scan...${NC}"
echo ""

semgrep --config=p/owasp-top-ten \
        --config=p/security-audit \
        --config=p/python \
        --config=p/django \
        --error \
        --severity=ERROR \
        --text \
        --exclude="**/tests.py" \
        --exclude="**/test_*.py" \
        --exclude="**/*_test.py" \
        --exclude="**/test/**" \
        --exclude="**/migrations/**" \
        --exclude="**/venv/**" \
        --exclude="**/env/**" \
        --exclude="**/.venv/**" \
        --exclude="**/__pycache__/**" \
        --exclude="**/*.md" \
        --exclude="**/*.sql" \
        --exclude="**/db.sqlite3" \
        .

# Check exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Semgrep scan completed successfully - no critical issues found${NC}"
else
    echo -e "${RED}✗ Semgrep scan found security issues${NC}"
    echo "Review the output above for details."
fi

exit $EXIT_CODE
