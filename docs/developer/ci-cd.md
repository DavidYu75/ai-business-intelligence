# CI/CD Pipeline Documentation

## Overview

The Real-Time BI Platform uses a comprehensive CI/CD pipeline built with GitHub Actions to ensure code quality, security, and reliable deployments.

## Pipeline Components

### 1. Main CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**

#### Backend Testing (`backend-test`)
- **Python Setup**: Python 3.11 with dependency caching
- **Services**: PostgreSQL 15 and Redis 7 for testing
- **Linting**: Black, isort, flake8, mypy
- **Testing**: pytest with 90% coverage requirement
- **Coverage**: Uploads to Codecov

#### Frontend Testing (`frontend-test`)
- **Node.js Setup**: Node.js 18 with npm caching
- **Linting**: ESLint, Prettier, TypeScript checking
- **Testing**: Jest with 80% coverage requirement
- **Coverage**: Uploads to Codecov

#### Security Scanning (`security-scan`)
- **Trivy**: Vulnerability scanning for dependencies and code
- **SARIF**: Results uploaded to GitHub Security tab

#### Docker Image Building (`build-images`)
- **Triggers**: Only on pushes to `main` branch
- **Registry**: GitHub Container Registry (ghcr.io)
- **Images**: Backend and frontend images with versioned tags
- **Dependencies**: Requires all tests and security scans to pass

#### Deployment (`deploy-staging`, `deploy-production`)
- **Staging**: Deploys from `develop` branch
- **Production**: Deploys from `main` branch
- **Environments**: Protected environments with approval workflows

#### Performance Testing (`performance-test`)
- **Tool**: Locust for load testing
- **Triggers**: Only on pushes to `main` branch

#### Failure Notification (`notify-failure`)
- **Triggers**: When any job fails
- **Purpose**: Send notifications to team members

### 2. Dependency Review (`.github/workflows/dependency-review.yml`)

- **Triggers**: Pull requests
- **Purpose**: Automatically review dependency changes for security issues
- **Severity**: Fails on moderate or higher severity issues

### 3. CodeQL Analysis (`.github/workflows/codeql-analysis.yml`)

- **Triggers**: Push to main, pull requests, weekly schedule
- **Languages**: Python and JavaScript
- **Purpose**: Advanced security analysis using GitHub's CodeQL engine

## Local Development

### Pre-commit Hooks

Install pre-commit hooks for local code quality checks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
make install-hooks

# Run on all files
make pre-commit-all
```

### Local Testing

Run the full CI/CD pipeline locally:

```bash
# Run all tests and linting
make ci-cd

# Run specific components
make lint          # Linting only
make test-backend  # Backend tests only
make test-frontend # Frontend tests only
make security-scan # Security scanning only
```

### Manual Testing Commands

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html
black --check --diff .
isort --check-only --diff .
flake8 .
mypy .

# Frontend
cd frontend
npm run test:coverage
npm run lint
npm run format:check
npm run type-check
```

## Configuration Files

### Backend Testing (`backend/pytest.ini`)
- Coverage threshold: 90%
- Async test support
- Custom markers for different test types
- Warning filters

### Frontend Testing (`frontend/jest.config.js`)
- Coverage threshold: 80%
- Next.js integration
- TypeScript support
- Custom test matching patterns

### Pre-commit (`pre-commit-config.yaml`)
- Python formatting (Black, isort, flake8, mypy)
- JavaScript/TypeScript linting (ESLint, Prettier)
- Security scanning (Bandit)
- Docker linting (Hadolint)
- Terraform validation (if applicable)

### Dependabot (`.github/dependabot.yml`)
- Weekly dependency updates
- Multiple ecosystems (pip, npm, GitHub Actions, Docker)
- Automatic PR creation with reviewers

## Environment Variables

### Required Secrets

Set these in your GitHub repository settings:

```bash
# GitHub Container Registry
GITHUB_TOKEN  # Automatically provided

# Deployment (if using external services)
KUBECONFIG_BASE64  # Kubernetes config for deployment
AWS_ACCESS_KEY_ID  # AWS credentials (if applicable)
AWS_SECRET_ACCESS_KEY
```

### Environment-Specific Variables

```bash
# Staging Environment
STAGING_DATABASE_URL
STAGING_REDIS_URL
STAGING_SECRET_KEY

# Production Environment
PRODUCTION_DATABASE_URL
PRODUCTION_REDIS_URL
PRODUCTION_SECRET_KEY
```

## Deployment Strategy

### Staging Deployment
- **Trigger**: Push to `develop` branch
- **Environment**: Staging environment
- **Approval**: Optional (can be configured)
- **Purpose**: Integration testing and QA

### Production Deployment
- **Trigger**: Push to `main` branch
- **Environment**: Production environment
- **Approval**: Required (protected environment)
- **Purpose**: Live user-facing deployment

### Rollback Strategy
- **Automatic**: Health check failures trigger rollback
- **Manual**: GitHub Actions UI allows manual rollback
- **Database**: Separate backup and restore procedures

## Monitoring and Alerting

### Pipeline Monitoring
- **Success Rate**: Track pipeline success/failure rates
- **Build Time**: Monitor build and test duration
- **Coverage Trends**: Track code coverage over time

### Deployment Monitoring
- **Health Checks**: Automated health checks after deployment
- **Performance Metrics**: Response time and error rate monitoring
- **User Impact**: Feature flag integration for gradual rollouts

## Best Practices

### Code Quality
1. **Test Coverage**: Maintain 90% backend, 80% frontend coverage
2. **Linting**: All code must pass linting checks
3. **Type Safety**: Use TypeScript and Python type hints
4. **Documentation**: Keep documentation updated with code changes

### Security
1. **Dependency Scanning**: Regular vulnerability scanning
2. **Code Analysis**: Static analysis with CodeQL
3. **Secret Management**: Use GitHub Secrets for sensitive data
4. **Access Control**: Limit deployment permissions

### Performance
1. **Build Optimization**: Cache dependencies and build artifacts
2. **Parallel Jobs**: Run independent jobs in parallel
3. **Resource Limits**: Set appropriate resource limits for jobs
4. **Monitoring**: Track pipeline performance metrics

## Troubleshooting

### Common Issues

#### Pipeline Failures
1. **Test Failures**: Check test logs for specific failures
2. **Linting Errors**: Run `make lint` locally to identify issues
3. **Coverage Issues**: Add tests to meet coverage requirements
4. **Security Issues**: Address vulnerability warnings

#### Deployment Issues
1. **Environment Variables**: Verify all required secrets are set
2. **Resource Limits**: Check for resource constraints
3. **Network Issues**: Verify connectivity to external services
4. **Permission Issues**: Check GitHub repository permissions

### Debugging Commands

```bash
# Check pipeline status
gh run list

# View specific run logs
gh run view <run-id>

# Rerun failed jobs
gh run rerun <run-id>

# Download artifacts
gh run download <run-id>
```

## Future Enhancements

### Planned Improvements
1. **Multi-environment Testing**: Test against multiple database types
2. **Performance Regression Testing**: Automated performance benchmarks
3. **Chaos Engineering**: Automated failure testing
4. **Blue-Green Deployments**: Zero-downtime deployment strategy
5. **Feature Flags**: Integration with feature flag management

### Monitoring Enhancements
1. **Real-time Alerts**: Slack/email notifications for failures
2. **Metrics Dashboard**: Pipeline performance visualization
3. **Cost Optimization**: Resource usage monitoring and optimization
4. **Security Dashboard**: Vulnerability trend analysis

## Support

For issues with the CI/CD pipeline:

1. Check the [GitHub Actions documentation](https://docs.github.com/en/actions)
2. Review pipeline logs for specific error messages
3. Consult the troubleshooting section above
4. Create an issue in the repository with detailed error information
