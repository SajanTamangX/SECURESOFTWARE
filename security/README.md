# Security Testing Directory

This directory contains security testing tools and scripts for the Phishing Simulation & Awareness Portal.

## Contents

- **`run_zap_baseline.sh`**: Bash script to run OWASP ZAP baseline scans
- **`reports/`**: Directory where ZAP scan reports are saved (excluded from git by default)

## Quick Start

1. Ensure Django application is running
2. Run the scan script with appropriate target URL:
   ```bash
   # Local development (Django on host)
   bash security/run_zap_baseline.sh http://localhost:8000
   
   # macOS Docker (access host from container)
   bash security/run_zap_baseline.sh http://host.docker.internal:8000
   
   # Docker Compose (access web service)
   bash security/run_zap_baseline.sh http://web:8000
   ```
3. Review reports in `security/reports/`

**Note for macOS Docker users**: Use `http://host.docker.internal:8000` to access your host machine's Django server from within the Docker container.

For detailed documentation, see `docs/dast_owasp_zap.md`.