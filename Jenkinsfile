pipeline {
    agent any
    
    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        SONAR_HOST_URL = 'http://172.24.142.21:9000'
        SONAR_TOKEN = credentials('sonarqube_global_token')
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
                script {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install pytest pytest-cov pylint
                    '''
                }
            }
        }
        
        stage('Linting') {
            steps {
                script {
                    sh '''
                        . venv/bin/activate
                        pylint **/*.py --exit-zero --output-format=text --reports=y > pylint-report.txt || true
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    sh '''
                        . venv/bin/activate
                        # Start test database
                        docker-compose up -d db
                        sleep 10
                        
                        # Run tests with coverage
                        pytest --cov=. --cov-report=xml --cov-report=html --junitxml=test-results.xml || true
                    '''
                }
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
                script {
                    sh '''
                        docker-compose build
                    '''
                }
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
                script {
                    sh '''
                        docker-compose down || true
                        docker-compose up -d
                        
                        # Wait for services to be ready
                        sleep 15
                        
                        # Health check
                        curl -f http://localhost:8000/health || exit 1
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                sh 'docker-compose down || true'
            }
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