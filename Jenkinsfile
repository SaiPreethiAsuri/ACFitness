pipeline {
    agent any

    environment {
    IMAGE_NAME = 'acfitness'
    DOCKERHUB_USER = 'preethi08042001'
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
                    def gitTagResult = bat(
                        script: 'git describe --tags --abbrev=0',
                        returnStatus: true
                    )

                    if (gitTagResult == 0) {
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
            environment {
                DOCKER_BUILDKIT = '1' // enable BuildKit
            }
            steps {
                script {
                    // Build image with proxy environment
                    bat "docker build -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} ."

                    // Docker login using Jenkins credentials
                    withCredentials([usernamePassword(credentialsId: 'ed059747-9182-4b62-95ec-603c6b6ef10d', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        bat "docker login -u %DOCKER_USER% -p %DOCKER_PASS%"
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
