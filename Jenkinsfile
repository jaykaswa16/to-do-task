pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'jaykaswa16'            // <-- your Docker Hub username
        IMAGE          = "${DOCKERHUB_USER}/todo-app"
        TAG            = "v${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt pytest
                    python -m py_compile app.py
                    pytest -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t $IMAGE:$TAG -t $IMAGE:latest .'
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
                    sh 'docker push $IMAGE:$TAG'
                    sh 'docker push $IMAGE:latest'
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh 'sed "s|image: .*|image: $IMAGE:$TAG|" k8s/deployment.yaml | kubectl apply -f -'
                sh 'kubectl apply -f k8s/service.yaml'
                sh 'kubectl rollout status deployment/todo-app --timeout=120s'
            }
        }

        stage('Verify') {
            steps {
                sh 'kubectl get pods,deployment,svc'
                sh 'curl -sf http://$(minikube ip):30007 | head -n 15'
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
    }
}
