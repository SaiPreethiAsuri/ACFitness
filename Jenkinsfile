pipeline {
    agent any

    environment {
        IMAGE_NAME = 'acfitness'
        IMAGE_TAG = 'v1'
        DOCKERHUB_USER = 'yourdockerhubusername'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"C:\\Users\\saipr\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pip install -r requirements.txt'
            }
        }

        stage('Run Unit Tests') {
            steps {
                bat '"C:\\Users\\saipr\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pytest tests/ --maxfail=1 --disable-warnings -q'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t %DOCKERHUB_USER%/%IMAGE_NAME%:%IMAGE_TAG% ."
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying application to Kubernetes...'
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}
