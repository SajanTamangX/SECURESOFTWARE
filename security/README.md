# Security Testing Directory

This directory contains security testing tools and scripts for the Phishing Simulation & Awareness Portal.

## Contents

- **`run_zap_baseline.sh`**: Bash script to run OWASP ZAP baseline scans
- **`reports/`**: Directory where ZAP scan reports are saved (excluded from git by default)

## Quick Start

1. Ensure Django application is running at `http://localhost:8000`
2. Run the scan script: `./security/run_zap_baseline.sh`
3. Review reports in `security/reports/`

For detailed documentation, see `docs/dast_owasp_zap.md`.
