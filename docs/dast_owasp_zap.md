# Dynamic Application Security Testing (DAST) with OWASP ZAP

## Overview

**Dynamic Application Security Testing (DAST)** is a security testing methodology that analyzes running applications to identify security vulnerabilities. Unlike Static Application Security Testing (SAST), which examines source code, DAST tests applications in their running state, simulating real-world attack scenarios.

This document describes the DAST implementation for the Phishing Simulation & Awareness Portal using **OWASP ZAP (Zed Attack Proxy)**, an open-source security testing tool maintained by the OWASP Foundation.

## Why OWASP ZAP?

We selected OWASP ZAP for the following reasons:

1. **Industry Standard**: ZAP is widely recognized and used in the security testing community
2. **Open Source**: Free to use, suitable for academic coursework
3. **Comprehensive**: Covers OWASP Top 10 vulnerabilities including XSS, SQL injection, and input validation issues
4. **Docker-Based**: Easy to integrate into development workflows without complex local installations
5. **Baseline Scanning**: Provides safe, non-destructive scanning suitable for development environments
6. **Report Generation**: Produces detailed HTML and JSON reports suitable for documentation and evidence

## Prerequisites

Before running DAST scans, ensure the following:

1. **Docker** is installed and running
   - Installation: https://docs.docker.com/get-docker/
   - Verify: `docker --version`

2. **Django Application** is running and accessible
   - Local development: `http://localhost:8000`
   - Docker Compose: `http://web:8000` (when using docker-compose network)

3. **Sufficient Disk Space**: Reports typically require 10-50MB per scan

## Running DAST Scans

### Method 1: Using the Convenience Script (Recommended)

The easiest way to run a DAST scan is using the provided script:

```bash
# Ensure Django app is running
# Option 1: Local development server
python manage.py runserver

# Option 2: Docker Compose
docker-compose up web

# In another terminal, run the ZAP scan
./security/run_zap_baseline.sh

# Or specify a custom target URL
./security/run_zap_baseline.sh http://web:8000
```

**What the script does:**
1. Checks Docker availability
2. Verifies target URL accessibility
3. Pulls the latest OWASP ZAP Docker image
4. Runs a baseline scan against the target URL
5. Generates timestamped HTML and JSON reports in `security/reports/`

### Method 2: Using Docker Compose

If using docker-compose, you can run ZAP as a service:

```bash
# Start the web application
docker-compose up -d web

# Run ZAP baseline scan
docker-compose run --rm zap zap-baseline.py \
  -t http://web:8000 \
  -r report.html \
  -J report.json \
  -I -j
```

### Method 3: Direct Docker Command

For more control, run ZAP directly:

```bash
docker run --rm \
  -v "$(pwd)/security/reports:/zap/wrk/:rw" \
  ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
  -t http://localhost:8000 \
  -r zap_report.html \
  -J zap_report.json \
  -I -j
```

## Understanding Scan Results

### Report Locations

After running a scan, reports are saved to:
- **HTML Report**: `security/reports/zap_baseline_YYYYMMDD_HHMMSS.html`
- **JSON Report**: `security/reports/zap_baseline_YYYYMMDD_HHMMSS.json`

### Risk Levels

ZAP categorizes findings by risk level:

- **High (3)**: Critical security issues requiring immediate attention
- **Medium (2)**: Important security issues that should be addressed
- **Low (1)**: Minor security concerns or best practice violations
- **Informational (0)**: Useful information but not security vulnerabilities

### Common Findings

The baseline scan focuses on common security issues relevant to input validation:

- **Cross-Site Scripting (XSS)**: Injection of malicious scripts
- **SQL Injection**: Database query manipulation
- **Missing Security Headers**: Absence of security-related HTTP headers
- **Insecure Cookie Settings**: Cookies without secure flags
- **Information Disclosure**: Exposure of sensitive information

## Scan Configuration

### Baseline Scan (Default)

The default scan uses ZAP's baseline mode, which is:
- **Safe**: Non-destructive, suitable for development environments
- **Fast**: Completes in 5-15 minutes depending on application size
- **Focused**: Targets common security vulnerabilities without aggressive fuzzing

### Excluded Paths

The scan automatically excludes:
- Static assets (`/static/`, `/admin/static/`)
- Media files (`/media/`)
- Admin interface (if desired, can be configured)

### Authenticated Scanning

**Note**: The current setup performs **non-authenticated scanning** by default. This is suitable for:
- Public-facing endpoints
- Login pages
- Registration forms
- General input validation testing

For authenticated scanning (testing protected endpoints), you can:
1. Configure ZAP context with authentication credentials
2. Use ZAP's authentication scripts
3. Provide session cookies or tokens

**Important**: Only configure authenticated scanning for your own controlled development environment. Never scan third-party systems without explicit authorization.

## Integration with Technical Security Assessment Report

### Evidence Collection

For your coursework report, include:

1. **Screenshot of Scan Execution**: Show the script running
2. **HTML Report Summary**: Include key findings and risk levels
3. **Risk Breakdown**: Number of High/Medium/Low findings
4. **Remediation Steps**: How you addressed identified issues

### Report Sections

Use DAST findings to support:

- **Input Validation Assessment**: XSS, SQL injection findings
- **Security Headers Analysis**: Missing security headers
- **Authentication & Session Management**: Cookie security issues
- **Error Handling**: Information disclosure findings

### Example Report Entry

```
DAST Methodology:
- Tool: OWASP ZAP Baseline Scan
- Target: http://localhost:8000
- Scan Date: [Date]
- Findings: 2 High, 5 Medium, 12 Low
- Key Issues: [List main findings]
- Remediation: [Actions taken]
```

## Security and Ethics

### Intended Use

This DAST setup is designed for:
- **Controlled Development Environments**: Your own project only
- **Educational Purposes**: Coursework security assessment
- **Non-Destructive Testing**: Baseline scans that won't damage data

### Restrictions

**DO NOT**:
- Scan third-party systems without authorization
- Use aggressive scanning modes that could disrupt services
- Share scan results publicly without sanitizing sensitive information
- Use findings to attack systems maliciously

### Responsible Disclosure

If you discover security issues:
1. Document findings appropriately
2. Address issues in your own codebase
3. For third-party dependencies, follow responsible disclosure practices

## Troubleshooting

### Common Issues

**Issue**: "Target URL not accessible"
- **Solution**: Ensure Django server is running and accessible at the target URL

**Issue**: "Docker command not found"
- **Solution**: Install Docker Desktop or Docker Engine

**Issue**: "Permission denied" when running script
- **Solution**: `chmod +x security/run_zap_baseline.sh`

**Issue**: Reports not generated
- **Solution**: Check Docker logs: `docker logs [container_id]`
- **Solution**: Verify `security/reports/` directory exists and is writable

### Getting Help

- OWASP ZAP Documentation: https://www.zaproxy.org/docs/
- ZAP Docker Hub: https://hub.docker.com/r/owasp/zap2docker-stable
- Project Issues: Check repository issues or contact course instructor

## Next Steps

1. **Run Initial Scan**: Execute baseline scan on your application
2. **Review Findings**: Analyze HTML report for security issues
3. **Address High/Medium Risks**: Fix critical vulnerabilities
4. **Re-scan**: Verify fixes by running another scan
5. **Document**: Include findings in your Technical Security Assessment Report

## References

- OWASP ZAP: https://www.zaproxy.org/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- DAST vs SAST: https://owasp.org/www-community/Source_Code_Analysis_Tools
- Docker Documentation: https://docs.docker.com/
