def call(dockerRepoName, imageName, portNum) {
    pipeline {
        agent any
        parameters {
            booleanParam(defaultValue: false, description: 'Deploy the App', name: 'DEPLOY')
        }
        stages {
            stage("Lint") {
                steps {
                    sh "pylint --fail-under=5.0 ./${dockerRepoName}/app.py"
                }
            }
            stage("Security") {
                steps {
                    sh "safety check -r ${dockerRepoName}/requirements.txt --full-report -o text --continue-on-error"
                }
            }
            stage("Package") {
            when {
                expression { env.GIT_BRANCH == 'origin/main' }
                    }
                    steps {
                    withCredentials([string(credentialsId: 'DockerHub', variable: 'TOKEN')]) {
                        sh "docker login -u 'shiole' -p '$TOKEN' docker.io"
                        sh "docker build -t ${dockerRepoName}:latest --tag shiole/${dockerRepoName}:${imageName} ."
                        sh "docker push shiole/${dockerRepoName}:${imageName}"
                    }
                }
            }
            stage("Deploy") {
                when {
                    expression { params.DEPLOY } 
                }
                steps {
                    sshagent(withCredentials([string(credentialsId: 'Kifka', variable: 'TOKEN')])) {
                        sh "cd ~/acit-3855-kafka/acit-3855-app/deployment && docker pull shiole/${dockerRepoName}:latest && docker-compose up -d"
                    }
                }
            }
        }
    }
}