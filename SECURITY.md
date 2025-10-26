# Security Policy

## Supported Versions

This project follows Python's maintenance schedule and supports versions that are actively maintained by the Python core team.

| Python Version | Supported          | End of Life |
| -------------- | ------------------ | ----------- |
| 3.14           | :white_check_mark: | Oct 2030    |
| 3.13           | :white_check_mark: | Oct 2029    |
| 3.12           | :white_check_mark: | Oct 2028    |
| 3.11           | :white_check_mark: | Oct 2027    |
| 3.10           | :x:                | Oct 2026    |
| < 3.10         | :x:                | EOL         |

## Security Features

This project implements the following security measures:

### Dependency Security
- **Dependabot**: Automatically monitors and updates dependencies
- **Regular Updates**: Dependencies are updated quarterly or when security issues are discovered
- **No Known Vulnerabilities**: All direct dependencies are free from known CVEs

### Code Security
- **CodeQL Scanning**: Automated security analysis on every commit
- **Secret Scanning**: Prevents accidental commit of secrets
- **Workflow Permissions**: GitHub Actions uses principle of least privilege

### Best Practices
- **No Hardcoded Secrets**: All sensitive data via environment variables
- **Password Masking**: Credentials never logged in plain text
- **Health Checks**: Docker containers have built-in health monitoring
- **Type Safety**: Static type checking with mypy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email the maintainer at: [Your preferred security contact email]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

You will receive a response within 48 hours acknowledging receipt. We will work with you to understand and address the issue promptly.

## Security Updates

Security updates are released as soon as possible after a vulnerability is confirmed:

- **Critical**: Within 24 hours
- **High**: Within 7 days
- **Medium/Low**: Next scheduled release

All security updates will be documented in [CHANGELOG.md](CHANGELOG.md) and announced via:
- GitHub Security Advisories
- Release notes
- Commit messages with `[SECURITY]` tag

## Security Audit History

| Date | Type | Findings | Status |
|------|------|----------|--------|
| 2025-10-26 | CodeQL | 6 issues (1 HIGH, 5 MEDIUM) | ✅ Resolved |
| 2025-10-26 | Dependency Audit | 0 vulnerabilities | ✅ Clear |

## Secure Development Practices

This project follows secure development practices:

- **Code Review**: All changes require review before merge
- **Automated Testing**: 92%+ test coverage with comprehensive test suite
- **CI/CD Security**: All builds run in isolated environments
- **Minimal Dependencies**: Only essential, well-maintained dependencies
- **Dependency Pinning**: Using `>=` version constraints for flexibility with security

## Additional Resources

- [Python Security](https://www.python.org/news/security/)
- [Redis Security](https://redis.io/docs/management/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
