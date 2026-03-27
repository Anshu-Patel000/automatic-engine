# Scan Report

- Repository: d:\MetaSphere\ms-aep-scanner-scanner\demo\github_repo_issue_demo\sample_repo_with_issues
- Total findings: 10
- Critical: 1
- High: 5
- Medium: 2
- Low: 2

## Findings

### 1. [SEC-HARDCODED-SECRET] Potential hardcoded secret/password found.
- Severity: critical
- File: d:\MetaSphere\ms-aep-scanner-scanner\demo\github_repo_issue_demo\sample_repo_with_issues\app.py:3
- Suggestion: Move secrets to environment variables or a secret manager.

### 2. [PY-DEBUG-PRINT] print() statement found in application code.
- Severity: low
- File: d:\MetaSphere\ms-aep-scanner-scanner\demo\github_repo_issue_demo\sample_repo_with_issues\app.py:7
- Suggestion: Use structured logging instead of print statements.

### 3. [PY-BARE-EXCEPT] Bare except detected.
- Severity: high
- File: d:\MetaSphere\ms-aep-scanner-scanner\demo\github_repo_issue_demo\sample_repo_with_issues\app.py:11
- Suggestion: Catch specific exceptions and log context.

### 4. [CODE-TODO] TODO marker found.
- Severity: low
- File: d:\MetaSphere\ms-aep-scanner-scanner\demo\github_repo_issue_demo\sample_repo_with_issues\app.py:16
- Suggestion: Track work in issues and remove stale TODO comments.

### 5. [AEP-142] Path '/Orders' contains uppercase characters.
- Severity: medium
- File: d:\MetaSphere\ms-aep-scanner-scanner\demo\github_repo_issue_demo\sample_repo_with_issues\openapi.yaml:6
- Suggestion: Use lowercase path segments for consistency.

### 6. [AEP-132] Missing operationId for GET /Orders.
- Severity: high
- File: d:\MetaSphere\ms-aep-scanner-scanner\demo\github_repo_issue_demo\sample_repo_with_issues\openapi.yaml:7
- Suggestion: Add a unique, stable operationId for every operation.

### 7. [AEP-132] Missing operationId for POST /Orders.
- Severity: high
- File: d:\MetaSphere\ms-aep-scanner-scanner\demo\github_repo_issue_demo\sample_repo_with_issues\openapi.yaml:12
- Suggestion: Add a unique, stable operationId for every operation.

### 8. [AEP-142] Path '/orders/{orderId}' contains uppercase characters.
- Severity: medium
- File: d:\MetaSphere\ms-aep-scanner-scanner\demo\github_repo_issue_demo\sample_repo_with_issues\openapi.yaml:23
- Suggestion: Use lowercase path segments for consistency.

### 9. [AEP-132] Missing operationId for GET /orders/{orderId}.
- Severity: high
- File: d:\MetaSphere\ms-aep-scanner-scanner\demo\github_repo_issue_demo\sample_repo_with_issues\openapi.yaml:7
- Suggestion: Add a unique, stable operationId for every operation.

### 10. [AEP-147] GET /orders/{orderId} defines requestBody.
- Severity: high
- File: d:\MetaSphere\ms-aep-scanner-scanner\demo\github_repo_issue_demo\sample_repo_with_issues\openapi.yaml:14
- Suggestion: Remove requestBody from GET and use query/path parameters instead.
