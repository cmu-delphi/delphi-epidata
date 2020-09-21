#!groovy

// import shared library: https://github.com/cmu-delphi/jenkins-shared-library
@Library('jenkins-shared-library') _

pipeline {

    agent any

    stages {

        stage('Deploy to AWS') {
            when {
                branch "main"
            }
            steps {
                sh "echo This is a temporary no-op. A Jenkins job called \
                         deploy-epidata-api-stack-aws is independently \
                         configured to run whenever this pipeline stage \
                         executes."
            }
        }
    }

    post {
        always {
            script {
                slackNotifier(currentBuild.currentResult)
            }
        }
    }
}