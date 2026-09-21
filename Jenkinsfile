pipeline {
    agent any

    parameters {
        choice(
            name: 'DEPLOYMENT_ACTION',
            choices: ['DEPLOY', 'ROLLBACK'],
            description: 'Deployment action'
        )

        choice(
            name: 'ENVIRONMENT',
            choices: ['UAT', 'PRODUCTION'],
            description: 'Target environment'
        )

        string(
            name: 'VERSION',
            defaultValue: '4.2.1',
            description: 'Application version'
        )

        choice(
            name: 'CONFIRM_PROD',
            choices: ['NO', 'YES'],
            description: 'Required for production deployment'
        )
    }

    stages {

        stage('Validate Parameters') {
            steps {
                script {
                    echo "Action      : ${params.DEPLOYMENT_ACTION}"
                    echo "Environment : ${params.ENVIRONMENT}"
                    echo "Version     : ${params.VERSION}"
                    echo "Prod Confirm: ${params.CONFIRM_PROD}"

                    if (params.ENVIRONMENT == 'PRODUCTION' &&
                        params.CONFIRM_PROD != 'YES') {
                        error("Production deployment requires CONFIRM_PROD=YES")
                    }
                }
            }
        }

        stage('Identify Git Commit') {
            steps {
                script {
                    def commit = bat(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Selected Git commit: ${commit}"
                }
            }
        }

        stage('Validate Version') {
            steps {
                script {
                    def tagExists = bat(
                        script: "git tag -l v${params.VERSION}",
                        returnStdout: true
                    ).trim()

                    if (!tagExists) {
                        error("Git tag v${params.VERSION} does not exist")
                    }

                    echo "Validated Git tag: v${params.VERSION}"
                }
            }
        }

        stage('Docker Build') {
            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {
                bat "docker build -t retail-app:${params.VERSION} ."
            }
        }

        stage('Deployment') {
    when {
        expression {
            params.DEPLOYMENT_ACTION == 'DEPLOY'
        }
    }

    steps {
        script {
            def containerName = "retail-app-uat"
            def networkName = "retail-network"

            echo "Deploying retail-app:${params.VERSION}"
            echo "Container: ${containerName}"
            echo "Network: ${networkName}"
            echo "Host port: 8081"

            bat "docker network inspect ${networkName} >nul 2>&1 || docker network create ${networkName}"

            bat "docker rm -f ${containerName} >nul 2>&1 || exit /b 0"

            bat """
                docker run -d ^
                --name ${containerName} ^
                --network ${networkName} ^
                -p 8081:8081 ^
                retail-app:${params.VERSION}
            """

            bat "docker ps"
        }
    }
}
    }

    post {
        success {
            echo "Pipeline completed successfully."
        }

        failure {
            echo "Pipeline failed."
        }
    }
}