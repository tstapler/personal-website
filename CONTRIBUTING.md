# Contributing Guide

## Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit pull request

## Testing Procedures

### Local Testing
- Run unit tests: `make test`
- Integration tests: `make integration`
- End-to-end tests: `make e2e`

### CI/CD Pipeline
All PRs must pass:
- Linting
- Unit tests
- Integration tests
- Security scans

## Code Standards
- Follow existing code style
- Include tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

## Review Process
1. Automated checks must pass
2. Code review required
3. Documentation review if needed
4. Final approval from maintainers
