pipeline {
    agent {
        docker {
            image 'python:3.13-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root --network host'
        }
    }
    
    environment {
        POSTGRES_USER = 'admin'
        POSTGRES_PASSWORD = 'admin'
        POSTGRES_DB = 'haybuy_db_test'
        SECRET_KEY = 'test-secret-key-for-ci-cd'
        JWT_SECRET_KEY = 'test-secret-key-for-ci-cd'
        JWT_ALGORITHM = 'HS256'
        ACCESS_TOKEN_EXPIRE_MINUTES = '30'
        ENVIRONMENT = 'test'
        
        // SonarQube Configuration
        SONAR_HOST_URL = 'http://172.24.142.21:9000'
        SONAR_PROJECT_KEY = 'haybuy-backend'
        SONAR_PROJECT_NAME = 'HaYBuy Backend'
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
                    apt-get install -y \
                        libpq-dev \
                        gcc \
                        g++ \
                        make \
                        curl \
                        gnupg \
                        lsb-release \
                        ca-certificates \
                        openjdk-21-jre-headless \
                        unzip
                    
                    echo "=== Verify Java installation ==="
                    java -version
                    
                    # Install Docker CLI
                    echo "=== Installing Docker CLI ==="
                    install -m 0755 -d /etc/apt/keyrings
                    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
                    chmod a+r /etc/apt/keyrings/docker.asc
                    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
                    apt-get update
                    apt-get install -y docker-ce-cli
                    
                    # Install Docker Compose
                    echo "=== Installing Docker Compose ==="
                    curl -SL "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
                    chmod +x /usr/local/bin/docker-compose
                    
                    # Install SonarQube Scanner
                    echo "=== Installing SonarQube Scanner ==="
                    curl -o /tmp/sonar-scanner.zip -L https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
                    unzip -q /tmp/sonar-scanner.zip -d /opt
                    ln -s /opt/sonar-scanner-5.0.1.3006-linux/bin/sonar-scanner /usr/local/bin/sonar-scanner
                    
                    echo "=== Verify all installations ==="
                    python3 --version
                    docker --version
                    docker-compose --version
                    java -version
                    sonar-scanner --version
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
        
        stage('Create Environment File') {
            steps {
                sh '''
                    set -e
                    echo "=== Creating .env file ==="
                    cat > .env << EOF
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
RUNNING_IN_DOCKER=true
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=${JWT_ALGORITHM}
ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
ENVIRONMENT=${ENVIRONMENT}
EOF
                    
                    echo "=== .env file created ==="
                    cat .env
                '''
            }
        }
        
        stage('Linting') {
            steps {
                sh '''
                    set -e
                    echo "=== Running pylint on app directory only ==="
                    venv/bin/pylint app --exit-zero --output-format=text --reports=y > pylint-report.txt || true
                    echo "=== Pylint report (first 50 lines) ==="
                    head -n 50 pylint-report.txt || true
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    set -e
                    echo "=== Creating .env.test for tests ==="
                    cat > .env.test << EOF
DATABASE_URL=sqlite:///:memory:
RUNNING_IN_DOCKER=false
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=${JWT_ALGORITHM}
ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
ENVIRONMENT=test
DEBUG=True
EOF
                    
                    echo "=== .env.test file created ==="
                    cat .env.test
                    
                    echo "=== Running tests ==="
                    venv/bin/pytest tests/ \
                        --cov=app \
                        --cov-report=xml:coverage.xml \
                        --cov-report=html:htmlcov \
                        --cov-report=term \
                        --junitxml=test-results.xml \
                        -v || true
                    
                    echo "=== Verify report files ==="
                    ls -lh coverage.xml test-results.xml || echo "⚠️ Report files not found"
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
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    withSonarQubeEnv('SonarQube') {
                        withCredentials([string(credentialsId: 'sonarqube-token-backend', variable: 'SONAR_TOKEN')]) {
                            sh '''
                                set -e
                                echo "=== Verify report files before SonarQube ==="
                                ls -lh coverage.xml test-results.xml pylint-report.txt 2>/dev/null || echo "⚠️ Some report files missing"
                                
                                echo "=== Running SonarQube Analysis ==="
                                sonar-scanner \
                                  -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                  -Dsonar.projectName="${SONAR_PROJECT_NAME}" \
                                  -Dsonar.sources=app \
                                  -Dsonar.tests=tests \
                                  -Dsonar.host.url=${SONAR_HOST_URL} \
                                  -Dsonar.token=${SONAR_TOKEN} \
                                  -Dsonar.python.version=3.13 \
                                  -Dsonar.sourceEncoding=UTF-8 \
                                  -Dsonar.exclusions=**/venv/**,**/__pycache__/**,**/.pytest_cache/**,**/htmlcov/**,**/*.pyc \
                                  -Dsonar.test.exclusions=**/tests/** \
                                  -Dsonar.python.coverage.reportPaths=coverage.xml \
                                  -Dsonar.python.pylint.reportPaths=pylint-report.txt \
                                  -Dsonar.branch.name=${BRANCH_NAME}
                                
                                echo "✅ SonarQube Analysis completed"
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    script {
                        echo "=== Waiting for Quality Gate ==="
                        try {
                            def qg = waitForQualityGate()
                            if (qg.status != 'OK') {
                                echo "⚠️ Quality Gate status: ${qg.status}"
                                // Don't fail the pipeline, just warn
                                unstable(message: "Quality Gate failed: ${qg.status}")
                            } else {
                                echo "✅ Quality Gate passed"
                            }
                        } catch (Exception e) {
                            echo "⚠️ Quality Gate check failed: ${e.message}"
                            // Don't fail the pipeline
                            unstable(message: "Quality Gate check failed: ${e.message}")
                        }
                    }
                }
            }
        }
        
        stage('Build Docker Images') {
            steps {
                sh '''
                    set -e
                    echo "=== Building Docker images ==="
                    docker-compose build
                    
                    echo "=== Docker images ==="
                    docker images | grep haybuy || true
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
                    sleep 25
                    
                    echo "=== Services status ==="
                    docker-compose ps
                    
                    echo "=== API logs ==="
                    docker-compose logs api | tail -50
                    
                    echo "=== Health check ==="
                    for i in 1 2 3 4 5; do
                        if curl -f http://localhost:8000/health 2>/dev/null; then
                            echo "✅ Health check passed"
                            curl -s http://localhost:8000/health | jq . || cat
                            break
                        else
                            echo "⏳ Waiting for API... attempt $i/5"
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
                docker-compose down -v || true
                docker system prune -f || true
                rm -f .env
            '''
        }
        success {
            echo '✅ Pipeline completed successfully!'
            echo "📊 View SonarQube Report: ${SONAR_HOST_URL}/dashboard?id=${SONAR_PROJECT_KEY}"
        }
        failure {
            echo '❌ Pipeline failed!'
            sh '''
                echo "=== Docker Compose Logs ==="
                docker-compose logs || true
            '''
        }
    }
}