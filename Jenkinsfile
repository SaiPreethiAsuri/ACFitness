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
                bat '"C:\\Users\\saipr\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pip install -r requirements.txt'
            }
        }

        stage('Run Unit Tests') {
            steps {
                bat '"C:\\Users\\saipr\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m pytest tests/ --maxfail=1 --disable-warnings -q'
            }
        }

        // 🔍 SonarQube Static Code Analysis
       stage('SonarQube Analysis') {
    steps {
        withSonarQubeEnv('sonarqube') {
            withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                bat """
                "C:\\Users\\saipr\\sonar-scanner-7.3.0.5189-windows-x64\\bin\\sonar-scanner.bat" ^
                -Dsonar.projectKey=acfitness ^
                -Dsonar.sources=. ^
                -Dsonar.host.url=http://localhost:9000 ^
                -Dsonar.token=%SONAR_TOKEN%
                """
            }
        }
    }
}
stage('Set Docker Tag') {
    steps {
        script {

            bat 'git fetch --all --tags'

            // Run tag fetch in PowerShell
            def raw = bat(
                script: 'powershell -NoProfile -Command "git tag --sort=-creatordate | Select-Object -Last 1"',
                returnStdout: true
            )

            // CLEAN: keep only the last non-empty line
            def clean = raw.readLines()
                           .findAll { it.trim() }          // remove empty lines
                           .last()                         // take the last clean line
                           .trim()                         // trim spaces

            // Ensure valid fallback
            if (!clean) clean = "latest"

            env.IMAGE_TAG = clean
            echo "✅ FINAL TAG: '${env.IMAGE_TAG}'"
        }
    }
}









        stage('Build & Push Docker Image') {
            environment {
                DOCKER_BUILDKIT = '1'
            }
            steps {
                script {
                    bat "docker build -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} ."

                    withCredentials([usernamePassword(credentialsId: 'ed059747-9182-4b62-95ec-603c6b6ef10d', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        bat "docker login -u %DOCKER_USER% -p %DOCKER_PASS%"
                        bat "docker tag ${env.IMAGE_NAME}:${env.IMAGE_TAG} %DOCKER_USER%/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                        bat "docker push %DOCKER_USER%/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                    }
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
