.PHONY: help semgrep-scan semgrep-install semgrep-install-pipx

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

semgrep-install: ## Install Semgrep using pip (recommended for CI/CD)
	@echo "Installing Semgrep via pip..."
	pip install semgrep

semgrep-install-pipx: ## Install Semgrep using pipx (recommended for local development)
	@echo "Installing Semgrep via pipx..."
	pipx install semgrep

semgrep-scan: ## Run Semgrep SAST scan on the project
	@echo "Running Semgrep SAST scan..."
	@if ! command -v semgrep &> /dev/null; then \
		echo "Error: Semgrep is not installed. Run 'make semgrep-install' or 'make semgrep-install-pipx' first."; \
		exit 1; \
	fi
	semgrep --config=p/owasp-top-ten --config=p/security-audit --config=p/python --config=p/django \
		--error --severity=ERROR \
		--exclude="**/tests.py" --exclude="**/test_*.py" --exclude="**/*_test.py" --exclude="**/test/**" \
		--exclude="**/migrations/**" --exclude="**/venv/**" --exclude="**/env/**" --exclude="**/.venv/**" \
		--exclude="**/__pycache__/**" --exclude="**/*.md" --exclude="**/*.sql" --exclude="**/db.sqlite3" \
		.

semgrep-scan-text: ## Run Semgrep scan with text output (for screenshots)
	@echo "Running Semgrep SAST scan (text output)..."
	@if ! command -v semgrep &> /dev/null; then \
		echo "Error: Semgrep is not installed. Run 'make semgrep-install' or 'make semgrep-install-pipx' first."; \
		exit 1; \
	fi
	semgrep --config=p/owasp-top-ten --config=p/security-audit --config=p/python --config=p/django \
		--error --severity=ERROR --text \
		--exclude="**/tests.py" --exclude="**/test_*.py" --exclude="**/*_test.py" --exclude="**/test/**" \
		--exclude="**/migrations/**" --exclude="**/venv/**" --exclude="**/env/**" --exclude="**/.venv/**" \
		--exclude="**/__pycache__/**" --exclude="**/*.md" --exclude="**/*.sql" --exclude="**/db.sqlite3" \
		.

semgrep-scan-json: ## Run Semgrep scan with JSON output
	@echo "Running Semgrep SAST scan (JSON output)..."
	@if ! command -v semgrep &> /dev/null; then \
		echo "Error: Semgrep is not installed. Run 'make semgrep-install' or 'make semgrep-install-pipx' first."; \
		exit 1; \
	fi
	semgrep --config=p/owasp-top-ten --config=p/security-audit --config=p/python --config=p/django \
		--error --severity=ERROR --json --output semgrep-results.json \
		--exclude="**/tests.py" --exclude="**/test_*.py" --exclude="**/*_test.py" --exclude="**/test/**" \
		--exclude="**/migrations/**" --exclude="**/venv/**" --exclude="**/env/**" --exclude="**/.venv/**" \
		--exclude="**/__pycache__/**" --exclude="**/*.md" --exclude="**/*.sql" --exclude="**/db.sqlite3" \
		.
