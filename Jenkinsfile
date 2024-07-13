@Library('Shared-lib') _

pipeline {
    agent any
    options {
        buildDiscarder(logRotator(daysToKeepStr: '30'))
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        APP_IMAGE_NAME ='app-image'
        WEB_IMAGE_NAME = 'web-image'
        DOCKER_COMPOSE_FILE = 'compose.yaml'
        DOCKER_REPO = 'ronn4/repo1'
        NEXUS_REPO = "Nexus"
        NEXUS_PROTOCOL = "http"
        NEXUS_URL = "172.20.30.109:8085"
        NEXUS_CREDENTIALS_ID = 'NEXUS_CREDENTIALS_ID'
        DOCKERHUB_CREDENTIALS = 'dockerhub'
        SNYK_API_TOKEN = 'SNYK_API_TOKEN'
    }

    stages {
        stage('Use Shared Library Code') {
            steps {
                echo 'Using Shared Library Code Stage...'
                helloWorld('DevOps Student')
                echo 'Completed Shared Library Code Stage'
            }
        }
        stage('Checkout and Extract Git Commit Hash') {
            steps {
                echo 'Starting Checkout Stage...'
                checkout scm
                echo 'Completed Checkout Stage'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Starting Docker Build Stage...'
                    try {
                        bat """
                            docker-compose -f ${DOCKER_COMPOSE_FILE} build
                        """
                        echo 'Docker Build Stage Completed'
                    } catch (Exception e) {
                        echo "Error in Docker Build Stage: ${e}"
                        throw e
                    }
                }
            }
        }
        stage('Login, Tag, and Push Images') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'NEXUS_CREDENTIALS_ID', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    script {
                        echo 'Starting Login, Tag, and Push Images Stage...'
                        try {
                            bat(script: 'git rev-parse --short HEAD > gitCommit.txt')
                            def GITCOMMIT = readFile('gitCommit.txt').trim()
                            def GIT_TAG = "${GITCOMMIT}"
                            def IMAGE_TAG = "v1.0.0-${BUILD_NUMBER}-${GIT_TAG}"
                            bat """
                                cd polybot
                                docker login -u ${USER} -p ${PASS} ${NEXUS_PROTOCOL}://${NEXUS_URL}/repository/${NEXUS_REPO}
                                docker tag ${APP_IMAGE_NAME}:latest ${NEXUS_URL}/${APP_IMAGE_NAME}:${IMAGE_TAG}
                                docker tag ${WEB_IMAGE_NAME}:latest ${NEXUS_URL}/${WEB_IMAGE_NAME}:${IMAGE_TAG}
                                docker push ${NEXUS_URL}/${APP_IMAGE_NAME}:${IMAGE_TAG}
                                docker push ${NEXUS_URL}/${WEB_IMAGE_NAME}:${IMAGE_TAG}
                            """
                            echo 'Login, Tag, and Push Images Stage Completed'
                        } catch (Exception e) {
                            echo "Error in Login, Tag, and Push Images Stage: ${e}"
                            throw e
                        }
                    }
                }
            }
        }
        stage('Security Vulnerability Scanning') {
            steps {
                script {
                    echo 'Starting Security Vulnerability Scanning Stage...'
                    try {
                        withCredentials([string(credentialsId: 'SNYK_API_TOKEN', variable: 'SNYK_TOKEN')]) {
                            bat """
                                snyk auth ${SNYK_TOKEN}
                                snyk container test ${APP_IMAGE_NAME}:latest --severity-threshold=high || exit 0
                            """
                        }
                        echo 'Security Vulnerability Scanning Stage Completed'
                    } catch (Exception e) {
                        echo "Error in Security Vulnerability Scanning Stage: ${e}"
                        throw e
                    }
                }
            }
        }
        stage('Install Python Requirements') {
            steps {
                script {
                    echo 'Starting Install Python Requirements Stage...'
                    try {
                        bat """
                            pip install --upgrade pip
                            pip install pytest unittest2 pylint flask telebot Pillow loguru matplotlib scikit-learn
                        """
                        echo 'Install Python Requirements Stage Completed'
                    } catch (Exception e) {
                        echo "Error in Install Python Requirements Stage: ${e}"
                        throw e
                    }
                }
            }
        }
        stage('Static Code Linting and Unittest') {
            parallel {
                stage('Static code linting') {
                    steps {
                        script {
                            echo 'Starting Static Code Linting Stage...'
                            try {
                                bat """
                                    python -m pylint -f parseable --reports=no polybot/*.py > pylint.log
                                    type pylint.log
                                """
                                echo 'Static Code Linting Stage Completed'
                            } catch (Exception e) {
                                echo "Error in Static Code Linting Stage: ${e}"
                                throw e
                            }
                        }
                    }
                }
                stage('Unittest') {
                    steps {
                        script {
                            echo 'Starting Unittest Stage...'
                            try {
                                bat 'python -m pytest --junitxml results.xml polybot/test'
                                echo 'Unittest Stage Completed'
                            } catch (Exception e) {
                                echo "Error in Unittest Stage: ${e}"
                                throw e
                            }
                        }
                    }
                }
            }
        }
        stage('Deployment to EC2') {
            steps {
                script {
                    echo 'Starting Deployment to EC2 Stage...'
                    try {
                        sshagent(['ec2-ssh-credentials']) {
                            bat """
                                ssh -o StrictHostKeyChecking=no ec2-user@ec2-3-72-58-99.eu-central-1.compute.amazonaws.com '
                                    docker pull ronn4/repo1:app
                                    docker stop app || true
                                    docker rm app || true
                                    docker run -d --name mypolybot-app -p 80:80 ronn4/repo1-app:latest
                                '
                            """
                        }
                        echo 'Deployment to EC2 Stage Completed'
                    } catch (Exception e) {
                        echo "Error in Deployment to EC2 Stage: ${e}"
                        throw e
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                echo 'Running post actions...'
                junit 'results.xml'
                recordIssues enabledForFailure: true, aggregatingResults: true
                recordIssues tools: [pyLint(pattern: 'pylint.log')]
                cleanWs(cleanWhenNotBuilt: false, deleteDirs: true, notFailBuild: true)
                bat """
                    docker image prune -f
                """
                echo 'Post actions completed'
            }
        }
    }
}
