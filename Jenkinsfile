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
            stage('Checkout') {
                steps {
                    git branch: '*/feat/setup-jenkinsfile', url: 'https://github.com/HaYBuy/haybuy-backend.git'
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

        stage('Run Tests & Coverage') {
            steps {
                sh '''
                  # กันปัญหา import app ไม่ได้
                  export PYTHONPATH="$WORKSPACE:${PYTHONPATH}"
                  fastapi-env/bin/pytest --maxfail=1 --disable-warnings -q --cov=app --cov-report=xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: '**/junit*.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('Sonarqube') {
                sh """
                    "${tool 'SonarScanner'}/bin/sonar-scanner" \
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