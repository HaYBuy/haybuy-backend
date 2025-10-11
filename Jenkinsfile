pipeline {
    agent any
    
    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        SONAR_HOST_URL = 'http://172.24.142.21:9000/'
        SONAR_TOKEN = credentials('sqa_9c6995dd00973421f299fd6024ceb3dc40c4c4fc')
        POSTGRES_USER = 'admin'
        POSTGRES_PASSWORD = 'admin'
        POSTGRES_DB = 'haybuy_db_test'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checked out successfully'
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3.13 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov pylint
                '''
            }
        }
        
        stage('Linting') {
            steps {
                sh '''
                    . venv/bin/activate
                    pylint **/*.py --exit-zero --output-format=text --reports=y > pylint-report.txt || true
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    # Start test database
                    docker-compose up -d db
                    sleep 10
                    
                    # Run tests with coverage
                    pytest --cov=. --cov-report=xml --cov-report=html --junitxml=test-results.xml || true
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                    publishHTML([
                        allowMissing: false,
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
                    def scannerHome = tool 'SonarQube Scanner'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=haybuy-backend \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=${SONAR_HOST_URL} \
                            -Dsonar.login=${SONAR_TOKEN} \
                            -Dsonar.python.coverage.reportPaths=coverage.xml \
                            -Dsonar.python.xunit.reportPath=test-results.xml \
                            -Dsonar.python.pylint.reportPaths=pylint-report.txt
                        """
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        
        stage('Build Docker Images') {
            steps {
                sh '''
                    docker-compose build
                '''
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'Dev'
            }
            steps {
                sh '''
                    docker-compose down
                    docker-compose up -d
                    
                    # Wait for services to be ready
                    sleep 15
                    
                    # Health check
                    curl -f http://localhost:8000/health || exit 1
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker-compose down || true'
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}