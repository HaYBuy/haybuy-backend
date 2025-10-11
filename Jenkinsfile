pipeline {
    agent {
        docker {
            image 'python:3.13-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root --network host'
        }
    }
    
    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        POSTGRES_USER = 'admin'
        POSTGRES_PASSWORD = 'admin'
        POSTGRES_DB = 'haybuy_db_test'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo '✅ Code checked out successfully'
            }
        }
        
        stage('Install System Dependencies') {
            steps {
                sh '''
                    set -e
                    echo "=== Installing system dependencies ==="
                    apt-get update
                    apt-get install -y curl gnupg lsb-release ca-certificates
                    
                    # Install Docker CLI
                    install -m 0755 -d /etc/apt/keyrings
                    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
                    chmod a+r /etc/apt/keyrings/docker.asc
                    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
                    apt-get update
                    apt-get install -y docker-ce-cli
                    
                    # Install Docker Compose
                    curl -SL "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
                    chmod +x /usr/local/bin/docker-compose
                    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
                    
                    echo "=== Verify installations ==="
                    python3 --version
                    docker --version
                    docker-compose --version
                '''
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                    set -e
                    echo "=== Setting up Python virtual environment ==="
                    python3 -m venv venv
                    
                    echo "=== Installing Python packages ==="
                    venv/bin/pip install --upgrade pip
                    venv/bin/pip install -r requirements.txt
                    venv/bin/pip install pytest pytest-cov pylint
                    
                    echo "=== Python packages installed ==="
                    venv/bin/pip list
                '''
            }
        }
        
        stage('Linting') {
            steps {
                sh '''
                    set -e
                    echo "=== Running pylint ==="
                    venv/bin/pylint **/*.py --exit-zero --output-format=text --reports=y > pylint-report.txt || true
                    echo "=== Pylint report ==="
                    head -n 50 pylint-report.txt || true
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    set -e
                    echo "=== Starting test database ==="
                    docker-compose up -d db
                    
                    echo "=== Waiting for database ==="
                    sleep 15
                    
                    echo "=== Database status ==="
                    docker-compose ps
                    
                    echo "=== Running tests ==="
                    venv/bin/pytest --cov=. --cov-report=xml --cov-report=html --junitxml=test-results.xml || true
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
        
        stage('Build Docker Images') {
            steps {
                sh '''
                    set -e
                    echo "=== Building Docker images ==="
                    docker-compose build
                '''
            }
        }
        
        stage('Deploy to Staging') {
            when {
                anyOf {
                    branch 'Dev'
                    branch 'feat/setup-jenkinsfile'
                    branch 'staging'
                }
            }
            steps {
                sh '''
                    set -e
                    echo "=== Deploying to staging ==="
                    docker-compose down || true
                    docker-compose up -d
                    
                    echo "=== Waiting for services ==="
                    sleep 20
                    
                    echo "=== Services status ==="
                    docker-compose ps
                    
                    echo "=== Health check ==="
                    for i in 1 2 3 4 5; do
                        if curl -f http://localhost:8000/health; then
                            echo "✅ Health check passed"
                            break
                        else
                            echo "⏳ Waiting for service... attempt $i/5"
                            sleep 5
                        fi
                    done
                '''
            }
        }
    }
    
    post {
        always {
            sh '''
                echo "=== Cleanup ==="
                docker-compose down || true
                docker system prune -f || true
            '''
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
            sh 'docker-compose logs || true'
        }
    }
}