@Library('shared-lib') _

pipeline {
    agent any
    options {
        // Keeps builds for the last 30 days.
        buildDiscarder(logRotator(daysToKeepStr: '30'))
        // Prevents concurrent builds of the same pipeline.
        disableConcurrentBuilds()
        // Adds timestamps to the log output.
        timestamps()
    }

    environment {
        // Define environment variables
        APP_IMAGE_NAME = 'app-image'
        WEB_IMAGE_NAME = 'web-image'
        DOCKER_COMPOSE_FILE = 'compose.yaml'
        DOCKER_REPO = 'ronn4/repo1'
        NEXUS_REPO = "dockernexus"
        NEXUS_PROTOCOL = "http"
        NEXUS_URL = "172.30.134.43:8085"
        NEXUS_CREDENTIALS_ID = 'NEXUS_CREDENTIALS_ID'
        DOCKERHUB_CREDENTIALS = 'dockerhub'
        SNYK_API_TOKEN = 'SNYK_API_TOKEN'
    }

    stages {
        stage('Use Shared Library Code') {
            steps {
                // Use the helloWorld function from the shared library
                helloWorld('DevOps Student')
            }
        }
        stage('Checkout and Extract Git Commit Hash') {
            steps {
                // Checkout code
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker image using docker-compose
                    bat """
                        docker-compose -f ${DOCKER_COMPOSE_FILE} build
                    """
                }
            }
        }
        stage('Login, Tag, and Push Images') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'NEXUS_CREDENTIALS_ID', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    script {
                        // Extract Git commit hash
                        bat(script: 'git rev-parse --short HEAD > gitCommit.txt')
                        def GITCOMMIT = readFile('gitCommit.txt').trim()
                        def GIT_TAG = "${GITCOMMIT}"
                        def IMAGE_TAG = "v1.0.0-${BUILD_NUMBER}-${GIT_TAG}"
                        // Login to Dockerhub / Nexus repo and tag + push the images
                        bat """
                            cd polybot
                            docker login -u ${USER} -p ${PASS} ${NEXUS_PROTOCOL}://${NEXUS_URL}/repository/${NEXUS_REPO}
                            docker tag ${APP_IMAGE_NAME}:latest ${NEXUS_URL}/${APP_IMAGE_NAME}:${IMAGE_TAG}
                            docker tag ${WEB_IMAGE_NAME}:latest ${NEXUS_URL}/${WEB_IMAGE_NAME}:${IMAGE_TAG}
                            docker push ${NEXUS_URL}/${APP_IMAGE_NAME}:${IMAGE_TAG}
                            docker push ${NEXUS_URL}/${WEB_IMAGE_NAME}:${IMAGE_TAG}
                        """
                    }
                }
            }
        }
        stage('Security Vulnerability Scanning') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'SNYK_API_TOKEN', variable: 'SNYK_TOKEN')]) {
                        // Scan the image
                        bat """
                            snyk auth $SNYK_TOKEN
                            snyk container test {APP_IMAGE_NAME}:latest --severity-threshold=high || exit 0
                        """
                    }
                }
            }
        }
        stage('Install Python Requirements') {
            steps {
                script {
                // Install Python dependencies
                bat """
                    pip install --upgrade pip
                    pip install pytest unittest2 pylint flask telebot Pillow loguru matplotlib
                """
                }
            }
        }
        stage('Static Code Linting and Unittest') {
            parallel {
                stage('Static code linting') {
                    steps {
                        script {
                            // Run python code analysis
                            bat """
                                python -m pylint -f parseable --reports=no polybot/*.py > pylint.log
                                type pylint.log
                            """
                        }
                    }
                }
                stage('Unittest') {
                    steps {
                        script {
                            // Run unittests
                            bat 'python -m pytest --junitxml results.xml polybot/test'
                        }
                    }
                }
            }
        }
        stage('Deployment to EC2') {
            steps {
                script {
                    sshagent(['ec2-ssh-credentials']) {
                        bat """
                            ssh -o StrictHostKeyChecking=no ec2-user@ec2-18-153-49-180.eu-central-1.compute.amazonaws.com '
                                docker pull ronn4/repo1-app:latest
                                docker stop mypolybot-app || true
                                docker rm mypolybot-app || true
                                docker run -d --name mypolybot-app -p 80:80 ronn4/repo1-app:latest
                            '
                        """
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                // Process the test results using the JUnit plugin
                junit 'results.xml'

                // Process the pylint report using the Warnings Plugin
                recordIssues enabledForFailure: true, aggregatingResults: true
                recordIssues tools: [pyLint(pattern: 'pylint.log')]

                // Clean up workspace after build
                cleanWs(cleanWhenNotBuilt: false,
                        deleteDirs: true,
                        notFailBuild: true)

                // Clean up unused dangling Docker images
                bat """
                    docker image prune -f
                """
            }
        }
    }
}