pipeline {
    agent any

    environment {
        IMAGE_NAME = 'acfitness'
        DOCKERHUB_USER = 'preethi08042001'
        IMAGE_TAG = 'latest'  // default, will be overridden if Git tag exists
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
                bat '"C:\\Users\\saipr\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pip install --user -r requirements.txt'
            }
        }

        stage('Run Unit Tests') {
            steps {
                bat '"C:\\Users\\saipr\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pytest tests/ --maxfail=1 --disable-warnings -q'
            }
        }

        stage('Set Docker Tag') {
            steps {
                script {
                    // Try to get the latest Git tag
                    def gitTagStatus = bat(script: 'git describe --tags --abbrev=0', returnStatus: true)

                    if (gitTagStatus == 0) {
                        env.IMAGE_TAG = bat(
                            script: 'git describe --tags --abbrev=0',
                            returnStdout: true
                        ).trim()
                    } else {
                        env.IMAGE_TAG = 'latest'
                    }

                    echo "Docker tag set to: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
                    // Login, build, tag, and push in one block
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        // Docker login
                        bat "echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin"

                        // Build Docker image
                        bat "docker build -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} ."

                        // Tag and push to Docker Hub
                        bat "docker tag ${env.IMAGE_NAME}:${env.IMAGE_TAG} %DOCKER_USER%/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                        bat "docker push %DOCKER_USER%/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                    }
                }
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
