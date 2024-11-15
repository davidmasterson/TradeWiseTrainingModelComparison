pipeline {
    agent any

    environment {
        PROJECT_DIR = '/home/ubuntu/TradeWiseTrainingModelComparison'
        CONDA_ENV = 'tf-env'
        CONDA_PATH = '/home/ubuntu/miniconda3'
    }

    stages {
        stage('Test Shell Access') {
            steps {
                script {
                    echo 'Testing shell access...'
                    sh 'echo Hello from the shell'
                }
            }
        }

        stage('Set Up Conda Environment') {
            steps {
                script {
                    // Run the setup commands as the ubuntu user to ensure correct permissions
                    sh """#!/bin/bash
                        sudo -u ubuntu bash -c '
                        source ${CONDA_PATH}/etc/profile.d/conda.sh
                        conda activate ${CONDA_ENV}
                        conda env update -f ${PROJECT_DIR}/environment.yaml --prune
                        '
                    """
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    // Run test commands as the ubuntu user
                    sh """#!/bin/bash
                        sudo -u ubuntu bash -c '
                        source ${CONDA_PATH}/etc/profile.d/conda.sh
                        conda activate ${CONDA_ENV}
                        # Run test commands here
                        '
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "Deploying application..."
                    sh "sudo systemctl stop tradewise.service"
                    sh "sudo cp -r ${PROJECT_DIR} /var/www/tradewise"
                    sh "sudo systemctl daemon-reload"
                    sh "sudo systemctl start tradewise.service"
                    sh "sudo systemctl enable tradewise.service"
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
            echo 'Build, Test, and Deployment steps are completed.'
        }
    }
}
