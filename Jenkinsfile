pipeline {
    agent any

    environment {
        IMAGE_NAME = "flask-fitness-app"
        IMAGE_TAG = "v1"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out code..."
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo "Running tests..."
                sh 'pytest tests/ --maxfail=1 --disable-warnings -q'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image locally..."
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo "Deploying to Kubernetes..."
                sh 'kubectl apply -f k8s/deployment.yaml'
                sh 'kubectl apply -f k8s/service.yaml'
            }
        }
    }

    post {
        success {
            echo '✅ CI/CD pipeline executed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}