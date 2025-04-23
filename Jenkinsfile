#!groovy


pipeline {
    agent any
    stages {
        stage("Build and up") {
            steps {
                sh "cp /home/romakot/workspace/envs/openaiimage-api.env .env"
                sh "docker compose up -d --build"
            }
        }
    }
}
