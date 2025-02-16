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

### Shortcode Documentation

#### Bibliography System
```markdown
{{</* bibliography file="references.bib" */>}}
<!-- or inline -->
{{</* bibliography */>}}
@article{mykey,
  title = {Example Title},
  author = {Author},
  year = {2023},
  url = {https://example.com}
}
{{</* /bibliography */>}}

Cite with: {{</* cite "mykey" */>}}
```

Required CSS:
```css
.bibliography { margin: 2rem 0; }
.bib-entry { margin: 1rem 0; display: flex; }
.bib-number { min-width: 3em; font-weight: bold; }
.citation { text-decoration: none; color: #0066cc; }
.citation:hover { text-decoration: underline; }
.bib-link { margin-left: 0.5rem; }
```

## Review Process
1. Automated checks must pass
2. Code review required
3. Documentation review if needed
4. Final approval from maintainers
