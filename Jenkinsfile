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
                    def gitTagResult = bat(script: 'git describe --tags --abbrev=0', returnStatus: true)

                    if (gitTagResult == 0) {
                        env.IMAGE_TAG = bat(script: 'git describe --tags --abbrev=0', returnStdout: true).trim()
                    } else {
                        env.IMAGE_TAG = 'latest'
                    }

                    echo "Docker tag set to: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Build & Push Docker Image') {
            environment {
                DOCKER_BUILDKIT = '1'
            }
            steps {
                script {
                    // Build image
                    bat "docker build -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} ."

                    // Docker login & push
                    withCredentials([usernamePassword(credentialsId: 'ed059747-9182-4b62-95ec-603c6b6ef10d', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        bat "docker login -u %DOCKER_USER% -p %DOCKER_PASS%"
                        bat "docker tag ${env.IMAGE_NAME}:${env.IMAGE_TAG} %DOCKER_USER%/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                        bat "docker push %DOCKER_USER%/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                    }
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                script {
                    echo "Deploying to local Minikube cluster..."
                    
                    // Update deployment.yaml image dynamically
                    bat "powershell -Command \"(Get-Content deployment.yaml) -replace 'image: .*', 'image: ${env.DOCKERHUB_USER}/${env.IMAGE_NAME}:${env.IMAGE_TAG}' | Set-Content deployment.yaml\""
                    
                    // Apply deployment in Minikube
                    bat "kubectl apply -f deployment.yaml"
                    
                    // Optional: expose service if not already exposed
                    bat "kubectl expose deployment acfitness --type=NodePort --name=acfitness-service || echo 'Service already exists'"
                    
                    // Get Minikube URL
                    bat "minikube service acfitness-service --url"
                }
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
