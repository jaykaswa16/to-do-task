
pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'jaykaswa16'
        IMAGE          = "${DOCKERHUB_USER}/todo-app"
        TAG            = "v${BUILD_NUMBER}"
        APP_VERSION    = "v${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Application Version: ${APP_VERSION}"
                echo "GitHub Commit: ${GIT_COMMIT}"
            }
        }

        stage('Build and Test') {
            steps {
                echo "Building and testing Application Version: ${APP_VERSION}"
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt pytest
                    python -m py_compile app.py
                    pytest -v
                '''
                echo "Build and Test completed for Version: ${APP_VERSION}"
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker Image: ${IMAGE}:${TAG}"
                sh 'docker build -t $IMAGE:$TAG -t $IMAGE:latest .'
                echo "Docker image built for Application Version: ${APP_VERSION}"
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_PASS'
                )]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker push "$IMAGE:$TAG"
                        docker push "$IMAGE:latest"
                    '''
                }
                echo "Pushed Docker Image: ${IMAGE}:${TAG}"
            }
        }

        stage('Deploy to Minikube') {
            steps {
                echo "Deploying Application Version: ${APP_VERSION}"
                sh 'sed "s|image: .*|image: $IMAGE:$TAG|" k8s/deployment.yaml | kubectl apply -f -'
                sh 'kubectl apply -f k8s/service.yaml'
                sh 'kubectl rollout status deployment/todo-app --timeout=120s'
                echo "Deployment completed for Version: ${APP_VERSION}"
            }
        }

        stage('Verify') {
            steps {
                echo "Verifying Application Version: ${APP_VERSION}"
                sh '''
                    kubectl get pods,deployment,svc
                    echo "Deployed container image:"
                    kubectl get deployment todo-app \
                      -o jsonpath='{.spec.template.spec.containers[0].image}'
                    echo
                    echo "Application Version: ${APP_VERSION}"
                    curl -sf http://$(minikube ip):30007 | head -n 15
                '''
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Application Version ${APP_VERSION} built, tested, pushed, and deployed."
        }
        failure {
            echo "FAILED: CI/CD pipeline for Application Version ${APP_VERSION}."
        }
        always {
            sh 'docker logout || true'
        }
    }
}
