def call(imageName) {
    pipeline {
        agent any
        parameters {
            booleanParam(defaultValue: false, description: 'Deploy the App', name: 'DEPLOY')
        }
        stages {
            stage("Lint") {
                steps {
                    sh "pylint --fail-under=5.0 ./${imageName}/*.py"
                }
            }
            stage("Security") {
                steps {
                    sh "safety check -r ${imageName}/requirements.txt --full-report -o text --continue-on-error"
                }
            }
            stage("Package") {
                steps {
                    withCredentials([string(credentialsId: 'DockerHub', variable: 'TOKEN')]) {
                        sh "docker login -u 'shiole' -p '$TOKEN' docker.io"
                        sh "docker build -t shiole/${imageName}:latest ${imageName}/."
                        sh "docker push shiole/${imageName}:latest"
                    }
                }
            }
            stage("Deploy") {
                when {
                    expression { params.DEPLOY } 
                }
                steps {
                    sshagent(withCredentials([string(credentialsId: 'kitty-kafka-ssh', variable: 'TOKEN')])) {
                        sh "ssh -o StrictHostKeyChecking=no azureuser@20.63.111.22 'cd ~/acit-3855-kafka/acit-3855-app/deployment && docker pull shiole/${imageName}:latest && docker-compose up -d'"
                    }
                }
            }
        }
    }
}