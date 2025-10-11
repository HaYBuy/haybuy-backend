# CI/CD Guide: Jenkins Docker-in-Docker with FastAPI and SonarQube

## Overview

This guide provides a complete setup for implementing Continuous Integration and Continuous Deployment (CI/CD) using Jenkins Docker-in-Docker architecture with FastAPI applications and SonarQube code quality analysis.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Installation and Setup](#installation-and-setup)
4. [Jenkins Configuration](#jenkins-configuration)
5. [SonarQube Integration](#sonarqube-integration)
6. [Pipeline Configuration](#pipeline-configuration)
7. [Running the Pipeline](#running-the-pipeline)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Prerequisites

- Docker Engine (v20.10.x or higher)
- Docker Compose (v2.0.x or higher)
- Git
- At least 4GB of available RAM
- Administrator/root access for Docker setup

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Developer     │    │     Jenkins     │    │    SonarQube    │
│                 │    │ (Docker-in-     │    │                 │
│ Push Code ────► │    │  Docker)        │    │ Quality Gate    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   FastAPI App   │
                       │    (Docker)     │
                       │                 │
                       └─────────────────┘
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/HayBuy/haybuy-backend.git
cd haybuy-backend
git checkout feat/setup-jenkinsfile
```

### 2. Directory Structure

Create the following directory structure:

```
haybuy-backend/
├── jenkins/
│   ├── Dockerfile
│   └── plugins.txt
├── docker-compose.yml
├── Jenkinsfile
├── sonar-project.properties
└── docs/
    └── CI_CD_GUIDE.md (this file)
```

### 3. Start the Services

```bash
# Start Jenkins and SonarQube
docker-compose up -d

# Check if services are running
docker-compose ps
```

### 4. Initial Jenkins Setup

1. Access Jenkins at `http://localhost:8080`
2. Get the initial admin password:
   ```bash
   docker-compose logs jenkins
   ```
3. Install suggested plugins
4. Create admin user
5. Configure Jenkins URL

### 5. Initial SonarQube Setup

1. Access SonarQube at `http://localhost:9000`
2. Default credentials: `admin/admin`
3. Change password when prompted
4. Create a new project
5. Generate authentication token

## Jenkins Configuration

### Required Plugins

The following plugins will be automatically installed via `plugins.txt`:
- Pipeline
- Docker Pipeline
- SonarQube Scanner
- Git
- Workspace Cleanup
- Build Timeout

### Jenkins Agent Configuration

Configure Jenkins to use Docker-in-Docker:

1. Go to `Manage Jenkins > Manage Nodes and Clouds`
2. Configure Docker as cloud provider
3. Set Docker Host URI: `unix:///var/run/docker.sock`

## SonarQube Integration

### 1. Configure SonarQube Server in Jenkins

1. Go to `Manage Jenkins > Configure System`
2. Find "SonarQube servers" section
3. Add SonarQube server:
   - Name: `SonarQube`
   - Server URL: `http://sonarqube:9000`
   - Server authentication token: (from SonarQube)

### 2. Install SonarQube Scanner

1. Go to `Manage Jenkins > Global Tool Configuration`
2. Add SonarQube Scanner installation
3. Name: `SonarQube Scanner`
4. Install automatically from Maven Central

## Pipeline Configuration

The Jenkins pipeline includes the following stages:

1. **Checkout**: Clone the repository
2. **Build**: Build the FastAPI application
3. **Test**: Run unit tests and generate coverage reports
4. **SonarQube Analysis**: Code quality analysis
5. **Quality Gate**: Wait for SonarQube quality gate result
6. **Docker Build**: Build Docker image
7. **Deploy**: Deploy to staging/production

### Environment Variables

Configure the following environment variables in Jenkins:

- `DOCKER_REGISTRY`: Docker registry URL
- `SONAR_TOKEN`: SonarQube authentication token
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Application secret key

## Running the Pipeline

### Manual Trigger

1. Access Jenkins dashboard
2. Click on your pipeline job
3. Click "Build Now"

### Automatic Trigger

Configure webhook in your Git repository:
- Webhook URL: `http://your-jenkins-url:8080/github-webhook/`
- Events: Push events, Pull request events

### Pipeline Status

Monitor pipeline execution:
- Build logs in Jenkins console
- SonarQube analysis results
- Test reports and coverage metrics
- Docker image build status

## Troubleshooting

### Common Issues

1. **Docker Permission Denied**
   ```bash
   sudo usermod -aG docker jenkins
   sudo systemctl restart jenkins
   ```

2. **SonarQube Connection Failed**
   - Check network connectivity between Jenkins and SonarQube containers
   - Verify SonarQube server URL and authentication token

3. **Pipeline Fails at Quality Gate**
   - Review SonarQube quality gate conditions
   - Check code coverage and code smells
   - Fix code quality issues

4. **Docker Build Fails**
   - Check Dockerfile syntax
   - Verify base image availability
   - Review build context and dependencies

### Log Locations

- Jenkins logs: `docker-compose logs jenkins`
- SonarQube logs: `docker-compose logs sonarqube`
- Application logs: Inside application container

## Best Practices

### Security

1. **Secrets Management**
   - Use Jenkins credentials store for sensitive data
   - Never hardcode passwords in Jenkinsfile
   - Rotate authentication tokens regularly

2. **Access Control**
   - Implement role-based access control
   - Use HTTPS in production
   - Regular security updates

### Performance

1. **Pipeline Optimization**
   - Use parallel stages where possible
   - Cache dependencies between builds
   - Clean up workspace after builds

2. **Resource Management**
   - Set appropriate memory limits for containers
   - Monitor disk usage
   - Implement log rotation

### Monitoring

1. **Build Metrics**
   - Track build success/failure rates
   - Monitor build duration trends
   - Set up notifications for failed builds

2. **Code Quality**
   - Set meaningful quality gate thresholds
   - Track technical debt trends
   - Regular code review practices

## Next Steps

1. **Production Deployment**
   - Configure production environment
   - Set up monitoring and alerting
   - Implement blue-green deployment

2. **Advanced Features**
   - Multi-branch pipeline
   - Automated testing strategies
   - Performance testing integration

3. **Scaling**
   - Jenkins agent scaling
   - Distributed builds
   - High availability setup

## Support

For additional support:
- Check Jenkins documentation: https://www.jenkins.io/doc/
- SonarQube documentation: https://docs.sonarqube.org/
- FastAPI documentation: https://fastapi.tiangolo.com/

---

**Last Updated**: 2025-10-11
**Version**: 1.0.0