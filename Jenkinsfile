pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'bert-legal-api'
        CONTAINER_NAME = 'bert-legal-api'
        PORT = '8005'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/mallelavamshi/bertapi.git'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker-compose build'
                }
            }
        }
        
        stage('Stop Existing Container') {
            steps {
                script {
                    sh '''
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true
                    '''
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    sh 'docker-compose up -d'
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    sh '''
                        echo "Waiting for service to start..."
                        sleep 30
                        curl -f http://localhost:8005/health || exit 1
                        echo "Service is healthy!"
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo 'Deployment successful!'
            echo 'API available at http://178.16.141.15:8005'
        }
        failure {
            echo 'Deployment failed!'
            sh 'docker-compose logs'
        }
    }
}
