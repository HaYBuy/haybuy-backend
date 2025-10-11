pipeline {
    agent {
        docker {
        image 'python:3.13'
        // รันเป็น root + เมานต์ docker.sock (ถ้าคุณยังต้องใช้ docker ภายหลัง)
        args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    options { timestamps() }


        
        stages {

            stage('Pre-clean git refs') {
  steps {
    sh '''
      set -eux
      git update-ref -d refs/remotes/origin/dev || true
      git remote prune origin || true
    '''
  }
}

            stage('Checkout') {
                steps {
                    git branch: 'feat/setup-jenkinsfile', url: 'https://github.com/HaYBuy/haybuy-backend.git'
                }
            }

            stage('Install Java 17 for Scanner') {
                steps {
                    sh '''
                    set -eux
                    apt-get update
                    apt-get install -y openjdk-21-jre-headless
                    java -version
                    '''
                }
                }

            stage('Install docker CLI') {
                steps {
                    sh '''
                    set -eux
                    apt-get update
                    # บน Debian trixie มีแพ็กเกจ docker.io ให้ใช้
                    apt-get install -y docker.io
                    docker version
                    '''
                }
            }

        stage('Setup venv') {
            steps {
                sh '''
                  python3 -m venv fastapi-env
                  . fastapi-env/bin/activate
                  pip install --upgrade pip
                  pip install -r requirements.txt
                '''
            }
        }

        stage('Start test DB') {
  steps {
    sh '''
      set -eux
      docker rm -f pg-test || true
      docker run -d --name pg-test \
        -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=haybuy_test \
        -p 5432:5432 postgres:15
      for i in {1..30}; do
        docker exec pg-test pg_isready -U postgres && break || sleep 2
      done
    '''
  }
}
stage('Run Tests & Coverage') {
  environment {
    DATABASE_URL = 'postgresql+psycopg2://postgres:postgres@localhost:5432/haybuy_test'
  }
  steps {
    sh '''
      set -eux
      export PYTHONPATH="${WORKSPACE}:${PYTHONPATH:-}"
      . fastapi-env/bin/activate
      pytest --maxfail=1 --disable-warnings -q \
        --cov=app --cov-report=xml \
        --junitxml=junit-report.xml
    '''
  }
}

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('Sonarqube') {
                sh """
                    "${tool 'Sonarqube'}/bin/sonar-scanner" \
                    -Dsonar.projectKey=sonarqube-haybuy \
                    -Dsonar.sources=app \
                    -Dsonar.tests=tests \
                    -Dsonar.python.coverage.reportPaths=coverage.xml
                """
                }
            }
        }

        
        // (ถ้าตั้ง Webhook ระหว่าง SonarQube -> Jenkins แล้ว ค่อยเปิดสเตจนี้)
        // stage('Quality Gate') {
        //     steps {
        //         timeout(time: 10, unit: 'MINUTES') {
        //             waitForQualityGate abortPipeline: true
        //         }
        //     }
        // }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t fastapi-app:latest .'
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                  # หยุด/ลบคอนเทนเนอร์เก่าถ้ามี เพื่อลดพอร์ตชน
                  docker rm -f fastapi-app || true
                  docker run -d --name fastapi-app -p 8000:8000 fastapi-app:latest
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline finished"
        }
    }
}