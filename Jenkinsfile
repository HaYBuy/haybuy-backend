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
                    echo "=== Installing system dependencies ==="
                    apt-get update
                    apt-get install -y curl gnupg lsb-release
                    
                    # Install Docker CLI
                    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
                    apt-get update
                    apt-get install -y docker-ce-cli
                    
                    # Install Docker Compose
                    curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                    chmod +x /usr/local/bin/docker-compose
                    
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
                    echo "=== Setting up Python virtual environment ==="
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov pylint
                    
                    echo "=== Python packages installed ==="
                    pip list
                '''
            }
        }
        
        stage('Linting') {
            steps {
                sh '''
                    . venv/bin/activate
                    echo "=== Running pylint ==="
                    pylint **/*.py --exit-zero --output-format=text --reports=y > pylint-report.txt || true
                    cat pylint-report.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    echo "=== Starting test database ==="
                    docker-compose up -d db
                    sleep 15
                    
                    echo "=== Database status ==="
                    docker-compose ps
                    
                    echo "=== Running tests ==="
                    pytest --cov=. --cov-report=xml --cov-report=html --junitxml=test-results.xml || true
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
                    echo "=== Deploying to staging ==="
                    docker-compose down || true
                    docker-compose up -d
                    
                    echo "=== Waiting for services ==="
                    sleep 20
                    
                    echo "=== Services status ==="
                    docker-compose ps
                    
                    echo "=== Health check ==="
                    curl -f http://localhost:8000/health || echo "Health check endpoint not available yet"
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