# CI/CD Security Pipeline Documentation

## Overview

This document describes the DevSecOps security pipeline implemented for the Phishing Simulation & Awareness Portal. The pipeline integrates multiple security testing tools into the continuous integration/continuous deployment (CI/CD) workflow, ensuring that security vulnerabilities are detected early in the development lifecycle.

## Pipeline Architecture

The security pipeline consists of five distinct jobs that run automatically on every push to `main`/`master` branches and on every pull request:

1. **Unit Tests** - Functional testing
2. **SAST (Semgrep)** - Static Application Security Testing
3. **Dependency Scanning (pip-audit)** - Vulnerability scanning for Python packages
4. **Secret Scanning (Gitleaks)** - Detection of hardcoded secrets
5. **DAST (OWASP ZAP)** - Dynamic Application Security Testing

## Job Descriptions

### 1. Unit Tests (`test`)

**Purpose**: Ensures that all Django unit tests pass before proceeding with security scans.

**What it does**:
- Sets up Python 3.11 environment
- Installs project dependencies from `requirements.txt`
- Configures PostgreSQL database service
- Runs database migrations
- Executes Django test suite using `python manage.py test`

**Why it's important**: Security scans should only run against functional code. If unit tests fail, it indicates the codebase is broken and security testing would be meaningless.

**Status**: **Security Gate** - Pipeline fails if tests don't pass.

---

### 2. SAST - Semgrep (`sast_semgrep`)

**Purpose**: Performs Static Application Security Testing (SAST) by analyzing source code for security vulnerabilities without executing the application.

**What it does**:
- Installs Semgrep security scanner
- Scans codebase using four official rulesets:
  - `p/owasp-top-ten` - OWASP Top 10 security vulnerabilities
  - `p/security-audit` - Generic security audit rules
  - `p/python` - Python-specific security rules
  - `p/django` - Django framework security rules
- Filters to HIGH/CRITICAL severity issues only (`--severity=ERROR`)
- Excludes test files, migrations, and build artifacts

**Why it's important**: SAST identifies security issues early in development, before code reaches production. It catches common vulnerabilities like SQL injection, XSS, insecure deserialization, and other OWASP Top 10 issues.

**Status**: **Security Gate** - Pipeline fails if HIGH/CRITICAL security issues are found.

**Integration**: This job runs after unit tests pass (`needs: test`).

---

### 3. Dependency Scanning - pip-audit (`dep_scan`)

**Purpose**: Scans Python dependencies listed in `requirements.txt` for known security vulnerabilities.

**What it does**:
- Installs `pip-audit` tool
- Scans all packages in `requirements.txt` against vulnerability databases
- Reports known Common Vulnerabilities and Exposures (CVEs)
- Provides descriptions of vulnerabilities and affected versions

**Why it's important**: Third-party dependencies often contain vulnerabilities that could be exploited. Keeping dependencies up-to-date and free of known vulnerabilities is critical for application security.

**Status**: **Security Gate** - Pipeline fails if vulnerable dependencies are detected.

**Integration**: This job runs after unit tests pass (`needs: test`).

---

### 4. Secret Scanning - Gitleaks (`secrets_scan`)

**Purpose**: Detects hardcoded secrets, API keys, passwords, tokens, and other sensitive information in the codebase.

**What it does**:
- Uses Gitleaks action to scan entire repository history
- Detects common secret patterns (API keys, passwords, tokens, etc.)
- Scans both current code and git history
- Reports any detected secrets

**Why it's important**: Hardcoded secrets in code repositories are a major security risk. If secrets are committed to version control, they can be exposed to unauthorized parties. This scan prevents accidental secret commits.

**Status**: **Security Gate** - Pipeline fails if secrets are detected.

**Integration**: This job runs after unit tests pass (`needs: test`).

---

### 5. DAST - OWASP ZAP Baseline (`dast_zap_baseline`)

**Purpose**: Performs Dynamic Application Security Testing (DAST) by testing the running application for security vulnerabilities.

**What it does**:
- Sets up Django application in CI environment
- Configures PostgreSQL database service
- Runs database migrations
- Starts Django development server on port 8000
- Executes OWASP ZAP baseline scan using `security/run_zap_baseline.sh`
- Generates HTML and JSON security reports
- Uploads reports as GitHub Actions artifacts

**Why it's important**: DAST tests the application in its running state, simulating real-world attack scenarios. It identifies vulnerabilities that SAST might miss, such as runtime configuration issues, authentication problems, and API security flaws.

**Status**: **Reporting Only** - This job does NOT fail the pipeline. Reports are generated and uploaded as artifacts for review. In a future iteration, we could parse the ZAP JSON reports and fail on Medium/High findings.

**Integration**: This job runs after unit tests pass (`needs: test`).

**Report Access**: ZAP reports can be downloaded from the GitHub Actions artifacts tab after the workflow completes.

---

## Security Gates

The following jobs act as **"hard gates"** that will block merges if they fail:

- ✅ **`test`** - Unit tests must pass
- ✅ **`sast_semgrep`** - No HIGH/CRITICAL security issues allowed
- ✅ **`dep_scan`** - No known vulnerabilities in dependencies
- ✅ **`secrets_scan`** - No hardcoded secrets allowed

The **`dast_zap_baseline`** job is currently configured as **non-blocking** (reporting only). This allows the pipeline to complete and generate reports even if security issues are found, enabling teams to review findings without blocking development.

### Future Enhancement

In a future iteration, the DAST job could be enhanced to:
- Parse ZAP JSON reports programmatically
- Extract risk levels (High, Medium, Low)
- Fail the pipeline if Medium or High risk findings are detected
- Provide detailed feedback on specific vulnerabilities found

---

## Pipeline Execution Flow

```
┌─────────────┐
│   Push/PR   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Unit Tests │ ◄─── Runs first
└──────┬──────┘
       │
       ├─────────────────┬─────────────────┬─────────────────┐
       ▼                 ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ SAST Semgrep │  │ Dep Scanning │  │ Secret Scan  │  │ DAST ZAP     │
│   (Gate)    │  │    (Gate)    │  │    (Gate)    │  │ (Reporting)  │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
       │                 │                 │                 │
       └─────────────────┴─────────────────┴─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Pipeline Status │
                    └─────────────────┘
```

---

## Accessing Reports

### ZAP DAST Reports

After the pipeline completes:

1. Go to **GitHub Actions** tab in your repository
2. Click on the workflow run
3. Scroll to the **Artifacts** section at the bottom
4. Download **`zap-baseline-report`** artifact
5. Extract the ZIP file to view HTML and JSON reports

**HTML Report**: Open `zap_baseline_*.html` in a web browser for human-readable findings.

**JSON Report**: Use `zap_baseline_*.json` for automated analysis or CI/CD integration.

### Other Job Outputs

- **Semgrep**: Findings are displayed directly in the GitHub Actions log
- **pip-audit**: Vulnerability details are shown in the job output
- **Gitleaks**: Secret detections are reported in the job output

---

## DevSecOps Integration

This pipeline implements **DevSecOps** principles by:

1. **Shift-Left Security**: Security testing happens early in the development lifecycle, not just before deployment
2. **Automated Security**: Security scans run automatically on every code change
3. **Fast Feedback**: Developers receive immediate feedback on security issues
4. **Security as Code**: Security policies are defined in version-controlled workflow files
5. **Continuous Monitoring**: Regular scanning ensures security posture is maintained

### Secure Software Development Lifecycle (SDLC)

The pipeline supports secure SDLC practices:

- **Requirements**: Security considerations are built into the development process
- **Design**: SAST helps identify design-level security issues
- **Implementation**: Real-time security feedback during development
- **Testing**: Comprehensive security testing (SAST, DAST, dependency scanning)
- **Deployment**: Security gates prevent vulnerable code from being merged
- **Maintenance**: Ongoing security monitoring through automated scans

---

## Branch Protection

To enforce security gates at the repository level:

1. Navigate to **Settings** > **Branches** in your GitHub repository
2. Click **Add rule** or edit existing rule for `main`/`master`
3. Enable **"Require status checks to pass before merging"**
4. Select the following required status checks:
   - `test`
   - `sast_semgrep`
   - `dep_scan`
   - `secrets_scan`
5. Optionally enable **"Require branches to be up to date before merging"**
6. Save changes

With branch protection enabled, pull requests cannot be merged until all security gates pass.

---

## Troubleshooting

### Common Issues

**Issue**: Unit tests fail
- **Solution**: Fix failing tests before security scans can run

**Issue**: Semgrep finds HIGH/CRITICAL issues
- **Solution**: Review findings, fix security vulnerabilities, commit fixes

**Issue**: pip-audit reports vulnerable dependencies
- **Solution**: Update vulnerable packages to patched versions in `requirements.txt`

**Issue**: Gitleaks detects secrets
- **Solution**: Remove secrets from code, rotate exposed credentials, use environment variables or secrets management

**Issue**: ZAP scan fails to start
- **Solution**: Check Django server logs in GitHub Actions output, ensure database migrations complete successfully

**Issue**: Reports not generated
- **Solution**: Check GitHub Actions artifacts section, verify `security/reports/` directory exists

---

## Best Practices

1. **Run Locally First**: Test changes locally before pushing to avoid pipeline failures
2. **Review Findings**: Don't just fix issues - understand why they occurred
3. **Update Dependencies**: Regularly update `requirements.txt` to get security patches
4. **Use Secrets Management**: Never hardcode secrets - use environment variables or secrets management tools
5. **Review ZAP Reports**: Download and review DAST reports regularly to identify runtime security issues
6. **Document Exceptions**: If a security finding is a false positive, document why and how to suppress it

---

## References

- **Semgrep**: https://semgrep.dev/
- **pip-audit**: https://pypi.org/project/pip-audit/
- **Gitleaks**: https://github.com/gitleaks/gitleaks
- **OWASP ZAP**: https://www.zaproxy.org/
- **DevSecOps**: https://www.devsecops.org/
- **GitHub Actions**: https://docs.github.com/en/actions

---

## Summary

This CI/CD security pipeline provides comprehensive security testing for the Phishing Simulation & Awareness Portal, integrating multiple security tools into an automated workflow. By implementing security gates and continuous scanning, we ensure that security vulnerabilities are detected and addressed early in the development process, supporting secure software development practices and DevSecOps principles.
