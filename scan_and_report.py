import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Allow imports from api-agent/scanners when run from workspace root.
CURRENT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = CURRENT_DIR.parent.parent
SCANNERS_DIR = WORKSPACE_ROOT / "api-agent" / "scanners"
sys.path.insert(0, str(SCANNERS_DIR))

from repo_scanner import RepositoryScanner  # noqa: E402
from file_detector import APIFileDetector  # noqa: E402


def line_number_for_pattern(lines: List[str], pattern: str) -> int:
    regex = re.compile(pattern)
    for idx, line in enumerate(lines, start=1):
        if regex.search(line):
            return idx
    return 1


def add_finding(
    findings: List[Dict[str, Any]],
    rule_id: str,
    severity: str,
    file_path: str,
    line: int,
    message: str,
    suggestion: str,
) -> None:
    findings.append(
        {
            "rule_id": rule_id,
            "severity": severity,
            "file": file_path,
            "line": line,
            "message": message,
            "suggestion": suggestion,
        }
    )


def scan_openapi_file(file_path: str, findings: List[Dict[str, Any]]) -> None:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        data = yaml.safe_load(content) or {}
    except Exception as exc:
        add_finding(
            findings,
            "PARSE-OPENAPI",
            "high",
            file_path,
            1,
            f"Failed to parse OpenAPI file: {exc}",
            "Fix YAML syntax and OpenAPI structure.",
        )
        return

    lines = content.splitlines()
    paths = data.get("paths", {})
    for path_key, ops in paths.items():
        if any(ch.isupper() for ch in path_key):
            add_finding(
                findings,
                "AEP-142",
                "medium",
                file_path,
                line_number_for_pattern(lines, re.escape(path_key)),
                f"Path '{path_key}' contains uppercase characters.",
                "Use lowercase path segments for consistency.",
            )

        if not isinstance(ops, dict):
            continue

        for method, operation in ops.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                continue

            if not isinstance(operation, dict):
                continue

            if "operationId" not in operation:
                add_finding(
                    findings,
                    "AEP-132",
                    "high",
                    file_path,
                    line_number_for_pattern(lines, rf"^\s*{method}:\s*$"),
                    f"Missing operationId for {method.upper()} {path_key}.",
                    "Add a unique, stable operationId for every operation.",
                )

            if method.lower() == "get" and "requestBody" in operation:
                add_finding(
                    findings,
                    "AEP-147",
                    "high",
                    file_path,
                    line_number_for_pattern(lines, r"^\s*requestBody:\s*$"),
                    f"GET {path_key} defines requestBody.",
                    "Remove requestBody from GET and use query/path parameters instead.",
                )


def scan_python_file(file_path: str, findings: List[Dict[str, Any]]) -> None:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()

    for idx, line in enumerate(lines, start=1):
        if re.search(r"^\s*except\s*:\s*$", line):
            add_finding(
                findings,
                "PY-BARE-EXCEPT",
                "high",
                file_path,
                idx,
                "Bare except detected.",
                "Catch specific exceptions and log context.",
            )

        if re.search(r"\bpassword\s*=\s*['\"][^'\"]+['\"]", line, re.IGNORECASE):
            add_finding(
                findings,
                "SEC-HARDCODED-SECRET",
                "critical",
                file_path,
                idx,
                "Potential hardcoded secret/password found.",
                "Move secrets to environment variables or a secret manager.",
            )

        if "print(" in line:
            add_finding(
                findings,
                "PY-DEBUG-PRINT",
                "low",
                file_path,
                idx,
                "print() statement found in application code.",
                "Use structured logging instead of print statements.",
            )

        if "TODO" in line:
            add_finding(
                findings,
                "CODE-TODO",
                "low",
                file_path,
                idx,
                "TODO marker found.",
                "Track work in issues and remove stale TODO comments.",
            )


def scan_text_file_for_common_markers(file_path: str, findings: List[Dict[str, Any]]) -> None:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()

    for idx, line in enumerate(lines, start=1):
        if "console.log(" in line:
            add_finding(
                findings,
                "JS-DEBUG-LOG",
                "low",
                file_path,
                idx,
                "console.log() found.",
                "Use an application logger with levels and context.",
            )
        if "TODO" in line:
            add_finding(
                findings,
                "CODE-TODO",
                "low",
                file_path,
                idx,
                "TODO marker found.",
                "Track work in issues and remove stale TODO comments.",
            )


def write_reports(output_dir: Path, repo_url: str, findings: List[Dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    issues_dir = output_dir / "issues"
    issues_dir.mkdir(parents=True, exist_ok=True)

    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = f["severity"].lower()
        by_severity[sev] = by_severity.get(sev, 0) + 1

    report_json = {
        "repo_url": repo_url,
        "total_findings": len(findings),
        "by_severity": by_severity,
        "findings": findings,
    }

    with open(output_dir / "scan_report.json", "w", encoding="utf-8") as f:
        json.dump(report_json, f, indent=2)

    md_lines = [
        "# Scan Report",
        "",
        f"- Repository: {repo_url}",
        f"- Total findings: {len(findings)}",
        f"- Critical: {by_severity.get('critical', 0)}",
        f"- High: {by_severity.get('high', 0)}",
        f"- Medium: {by_severity.get('medium', 0)}",
        f"- Low: {by_severity.get('low', 0)}",
        "",
        "## Findings",
        "",
    ]

    if not findings:
        md_lines.append("No issues found.")
    else:
        for i, finding in enumerate(findings, start=1):
            md_lines.extend(
                [
                    f"### {i}. [{finding['rule_id']}] {finding['message']}",
                    f"- Severity: {finding['severity']}",
                    f"- File: {finding['file']}:{finding['line']}",
                    f"- Suggestion: {finding['suggestion']}",
                    "",
                ]
            )

            issue_body = [
                f"# [{finding['rule_id']}] {finding['message']}",
                "",
                f"- Severity: {finding['severity']}",
                f"- File: {finding['file']}:{finding['line']}",
                "",
                "## Suggested Fix",
                finding["suggestion"],
                "",
                "## Source",
                "Generated by demo scan_and_report.py",
                "",
            ]
            issue_file = issues_dir / f"issue_{i:03d}_{finding['rule_id']}.md"
            with open(issue_file, "w", encoding="utf-8") as issue_f:
                issue_f.write("\n".join(issue_body))

    with open(output_dir / "scan_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo repo scanner with issue-style reporting")
    parser.add_argument("--repo-url", required=True, help="Git repository URL to scan")
    parser.add_argument("--temp-dir", default=str(CURRENT_DIR / "tmp" / "repo_scan"), help="Temp clone dir")
    parser.add_argument("--output-dir", default=str(CURRENT_DIR / "reports"), help="Directory for reports")
    args = parser.parse_args()

    scanner = RepositoryScanner(temp_dir=args.temp_dir)
    detector = APIFileDetector()

    # Extend include list for demo so app files and specs are always considered.
    detector.patterns["include"].extend(["*.py", "*.js", "*.ts", "*.yaml", "*.yml", "*.json"])

    print(f"Cloning repository: {args.repo_url}")
    repo_path = scanner.clone_repository(args.repo_url)
    if not repo_path:
        print("Failed to clone repository.")
        return

    print(f"Scanning repository path: {repo_path}")
    files = detector.scan_directory(repo_path)

    findings: List[Dict[str, Any]] = []

    for file_path in files:
        lower = file_path.lower()
        try:
            if lower.endswith(("openapi.yaml", "openapi.yml", "swagger.yaml", "swagger.yml")):
                scan_openapi_file(file_path, findings)
            elif lower.endswith(".py"):
                scan_python_file(file_path, findings)
            elif lower.endswith((".js", ".ts", ".tsx", ".jsx")):
                scan_text_file_for_common_markers(file_path, findings)
            elif lower.endswith((".yaml", ".yml", ".json")):
                scan_text_file_for_common_markers(file_path, findings)
        except Exception as exc:
            add_finding(
                findings,
                "SCAN-ERROR",
                "medium",
                file_path,
                1,
                f"Scan failed for file: {exc}",
                "Check parser logic and file format.",
            )

    output_dir = Path(args.output_dir)
    write_reports(output_dir, args.repo_url, findings)

    print("\nScan complete.")
    print(f"Total findings: {len(findings)}")
    print(f"Report JSON: {output_dir / 'scan_report.json'}")
    print(f"Report MD:   {output_dir / 'scan_report.md'}")
    print(f"Issue docs:  {output_dir / 'issues'}")


if __name__ == "__main__":
    main()
