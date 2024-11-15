pipeline {
    agent any

    environment {
        PROJECT_DIR = '/home/ubuntu/TradeWiseTrainingModelComparison'
        CONDA_ENV = 'tf-env'
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
            when {
                branch 'main'  // Only trigger this pipeline if changes are in the 'main' branch
            },
            steps {
                script {
                    // Activate the conda environment and install dependencies
                    sh """
                        source ~/miniconda3/etc/profile.d/conda.sh
                        conda activate ${CONDA_ENV}
                        conda env update -f ${PROJECT_DIR}/environment.yml --prune
                    """
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    sh """
                        source ~/miniconda3/etc/profile.d/conda.sh
                        conda activate ${CONDA_ENV}
                        # Run test commands here
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
            echo 'Build, Test and Deployment steps are completed.'
        }
    }
}
