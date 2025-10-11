pipeline {
  agent any
  stages {
    stage('Docker smoke test') {
      steps {
        sh 'docker version'
        sh 'docker run --rm hello-world'
      }
    }
  }
}
