pipeline {
    agent any

    environment {
        PROJECT_DIR = '/home/ubuntu/LSTMStockPricePredictor'
    }
        stage('Build') {
            steps {
                script {
                    sh 'env'
                    sh '#!/bin/bash -e \n echo "Running in bash"'
                    shellType = sh(script: 'echo $SHELL', returnStdout: true).trim()
                    echo "Current Shell: ${shellType}"
                    sh 'echo $SHELL'
                    echo "Installing dependencies..."
                    sh "${env.PROJECT_DIR}/venv/bin/python -m pip install -r ${env.PROJECT_DIR}/requirements.txt"
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    echo "Running unit tests..."
                    // Your testing commands will go here
                    // Just adding a comment to test the jenkins CI/CD with github
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "Deploying application..."
                    sh "sudo systemctl stop autotrader_project.service"
                    sh "sudo cp -r ${env.PROJECT_DIR} /var/www/autotrader_project"
                    sh "sudo systemctl daemon-reload"
                    sh "sudo systemctl start autotrader_project.service"
                    sh "sudo systemctl enable autotrader_project.service"
                    echo "Application deployed and service restarted successfully."
                    
                    echo "Reloading Nginx..."
                    sh "sudo systemctl reload nginx"
                    sh "sudo systemctl enable nginx"
                    echo "Nginx reloaded and enabled successfully."
                }
            }
        }
    }

    post {
        always {
            echo 'Build, Test and Deployment steps are completed.'
        }
    }
}
