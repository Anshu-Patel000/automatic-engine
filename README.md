# GitHub Repo Issue Demo

This demo helps you test a workflow where you provide a Git repository link, scan for code and AEP-style issues, and receive a report.

## What is included
- `sample_repo_with_issues/`: intentionally problematic files for demo
- `scan_and_report.py`: scanner script that clones a repo and creates issue reports

## Quick demo flow
1. Push `sample_repo_with_issues/` to your GitHub as a test repository.
2. Run the scanner with your repo URL:
   - `python demo/github_repo_issue_demo/scan_and_report.py --repo-url https://github.com/<owner>/<repo>.git`
3. Check output files:
   - `demo/github_repo_issue_demo/reports/scan_report.json`
   - `demo/github_repo_issue_demo/reports/scan_report.md`
   - `demo/github_repo_issue_demo/reports/issues/*.md`

## Rules checked in this demo
- OpenAPI operation missing `operationId` (AEP-132 style)
- `GET` operation using `requestBody` (AEP-147 style)
- Path contains uppercase characters (AEP-142 style)
- Python bare `except:`
- Hardcoded secrets/password assignment
- `print()` debug usage
- TODO markers

## Notes
- This is a demonstration scanner, not full production compliance automation.
- You can extend `scan_and_report.py` with more rules and GitHub issue API integration.
