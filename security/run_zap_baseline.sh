#!/bin/bash
# OWASP ZAP Baseline Scan Script
# 
# Purpose:
#   This script performs a Dynamic Application Security Testing (DAST) scan
#   using OWASP ZAP against the Django Phishing Simulation & Awareness Portal.
#   It is designed for coursework use in a controlled development environment.
#
# Prerequisites:
#   1. Docker must be installed and running
#   2. The Django application must be running and accessible at http://localhost:8000
#      (or http://web:8000 if running via docker-compose)
#   3. Sufficient disk space for scan reports (typically 10-50MB per scan)
#
# Usage:
#   ./security/run_zap_baseline.sh [target_url]
#
#   Default target URL: http://localhost:8000
#   Example: ./security/run_zap_baseline.sh http://web:8000
#
# Output:
#   Reports are saved to security/reports/ with timestamped filenames:
#   - zap_baseline_YYYYMMDD_HHMMSS.html (HTML report)
#   - zap_baseline_YYYYMMDD_HHMMSS.json (JSON report)
#
# Security Note:
#   This script is intended for scanning our own controlled development environment only.
#   Do NOT use this script to scan third-party systems without explicit authorization.

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TARGET_URL="${1:-http://localhost:8000}"
ZAP_IMAGE="ghcr.io/zaproxy/zaproxy:stable"
REPORTS_DIR="security/reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
HTML_REPORT="${REPORTS_DIR}/zap_baseline_${TIMESTAMP}.html"
JSON_REPORT="${REPORTS_DIR}/zap_baseline_${TIMESTAMP}.json"

# Ensure reports directory exists
mkdir -p "${REPORTS_DIR}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}OWASP ZAP Baseline Scan${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Target URL:${NC} ${TARGET_URL}"
echo -e "${YELLOW}ZAP Image:${NC} ${ZAP_IMAGE}"
echo -e "${YELLOW}Reports Directory:${NC} ${REPORTS_DIR}"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not in PATH${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if target URL is accessible (optional check)
echo -e "${YELLOW}Checking if target URL is accessible...${NC}"
if command -v curl &> /dev/null; then
    if curl -s --head --fail "${TARGET_URL}" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Target URL is accessible${NC}"
    else
        echo -e "${RED}✗ Warning: Target URL may not be accessible${NC}"
        echo "  Please ensure the Django application is running at ${TARGET_URL}"
        echo "  Continuing anyway..."
    fi
else
    echo -e "${YELLOW}Note: curl not found, skipping URL accessibility check${NC}"
    echo "  Please ensure the Django application is running at ${TARGET_URL}"
fi
echo ""

# Pull latest ZAP image (optional, but ensures we have the latest)
echo -e "${YELLOW}Pulling OWASP ZAP Docker image...${NC}"
docker pull "${ZAP_IMAGE}" || echo -e "${YELLOW}Warning: Could not pull image, using cached version${NC}"
echo ""

# Run ZAP baseline scan
# The baseline scan is a safe, non-intrusive scan suitable for coursework environments
# It focuses on common security issues without aggressive fuzzing that could damage data
echo -e "${YELLOW}Starting ZAP baseline scan...${NC}"
echo "This may take 5-15 minutes depending on application size..."
echo ""

# Run ZAP baseline scan using zap-baseline.py script
# -t: target URL
# -r: HTML report filename
# -J: JSON report filename  
# -I: ignore warnings (don't fail on warnings)
# -j: output JSON format
# -g: generate report (default)
docker run --rm \
    -v "$(pwd)/${REPORTS_DIR}:/zap/wrk/:rw" \
    "${ZAP_IMAGE}" zap-baseline.py \
    -t "${TARGET_URL}" \
    -r "zap_baseline_${TIMESTAMP}.html" \
    -J "zap_baseline_${TIMESTAMP}.json" \
    -I \
    -j \
    || {
        # ZAP baseline scan exits with non-zero code if issues are found
        # This is expected behavior - we still want to generate reports
        echo ""
        echo -e "${YELLOW}ZAP scan completed with findings (this is expected)${NC}"
    }

# Move reports from Docker volume to reports directory
# The reports are already in the right place due to volume mount, but verify
if [ -f "${REPORTS_DIR}/zap_baseline_${TIMESTAMP}.html" ]; then
    echo ""
    echo -e "${GREEN}✓ Scan completed successfully${NC}"
    echo ""
    echo -e "${BLUE}Report Files Generated:${NC}"
    echo -e "  HTML Report: ${GREEN}${HTML_REPORT}${NC}"
    echo -e "  JSON Report: ${GREEN}${JSON_REPORT}${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Review the HTML report: open ${HTML_REPORT} in a web browser"
    echo "  2. Use the JSON report for automated analysis or CI/CD integration"
    echo "  3. Address any HIGH or CRITICAL findings identified in the scan"
    echo "  4. Include key findings in your Technical Security Assessment Report"
    echo ""
else
    echo -e "${RED}Error: Report files were not generated${NC}"
    echo "Check the Docker output above for error messages"
    exit 1
fi

# Optional: Display summary of findings from JSON report
if command -v jq &> /dev/null && [ -f "${JSON_REPORT}" ]; then
    echo -e "${BLUE}Scan Summary:${NC}"
    HIGH_COUNT=$(jq '[.site[] | .alerts[] | select(.riskcode == "3")] | length' "${JSON_REPORT}" 2>/dev/null || echo "0")
    MEDIUM_COUNT=$(jq '[.site[] | .alerts[] | select(.riskcode == "2")] | length' "${JSON_REPORT}" 2>/dev/null || echo "0")
    LOW_COUNT=$(jq '[.site[] | .alerts[] | select(.riskcode == "1")] | length' "${JSON_REPORT}" 2>/dev/null || echo "0")
    INFO_COUNT=$(jq '[.site[] | .alerts[] | select(.riskcode == "0")] | length' "${JSON_REPORT}" 2>/dev/null || echo "0")
    
    echo -e "  High Risk:    ${RED}${HIGH_COUNT}${NC}"
    echo -e "  Medium Risk:  ${YELLOW}${MEDIUM_COUNT}${NC}"
    echo -e "  Low Risk:     ${BLUE}${LOW_COUNT}${NC}"
    echo -e "  Informational: ${GREEN}${INFO_COUNT}${NC}"
    echo ""
fi

echo -e "${GREEN}DAST scan complete!${NC}"
