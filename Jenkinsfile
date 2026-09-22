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

        stage('Validate Version') {
            steps {
                script {
                    def tagFile = "git-tag.txt"

                    bat """
                        git tag -l v${params.VERSION} > ${tagFile}
                    """

                    def tagExists = readFile(tagFile).trim()

                    bat "del /q ${tagFile} >nul 2>&1 || exit /b 0"

                    if (!tagExists) {
                        error("Git tag v${params.VERSION} does not exist")
                    }

                    echo "Validated Git tag: v${params.VERSION}"
                }
            }
        }
	stage('Checkout Requested Version') {
    steps {
        script {
            echo "Checking out requested version: v${params.VERSION}"

            bat """
                git fetch --tags
                git checkout --detach v${params.VERSION}
            """

            echo "Checked out Git tag: v${params.VERSION}"
        }
    }
}
stage('Identify Git Commit') {
            steps {
                script {
                    def commitFile = "git-commit.txt"

                    bat """
                        git rev-parse HEAD > ${commitFile}
                    """

                    def commit = readFile(commitFile).trim()

                    echo "Selected Git commit: ${commit}"

                    bat "del /q ${commitFile} >nul 2>&1 || exit /b 0"
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
            def candidateName = "retail-app-candidate"
            def networkName = "retail-network"
            def oldImage = "NONE"

            def containerExists = bat(
                script: "docker inspect ${containerName} >nul 2>&1",
                returnStatus: true
            )

            if (containerExists == 0) {
                bat """
                    docker inspect --format="{{.Config.Image}}" ${containerName} > old-image.txt
                """

                oldImage = readFile("old-image.txt").trim()

                bat "del /q old-image.txt >nul 2>&1 || exit /b 0"
            }

            if (!oldImage || oldImage == "") {
                oldImage = "NONE"
            }

            echo "Previous UAT image: ${oldImage}"
            echo "New image: retail-app:${params.VERSION}"

            env.OLD_IMAGE = oldImage

            echo "Starting candidate container..."
            echo "Candidate: ${candidateName}"
            echo "Candidate port: 8082"

            bat """
                docker network inspect ${networkName} >nul 2>&1 || docker network create ${networkName}
            """

            bat """
                docker rm -f ${candidateName} >nul 2>&1 || exit /b 0
            """

            bat """
                docker run -d ^
                --name ${candidateName} ^
                --network ${networkName} ^
                -p 8082:8081 ^
                retail-app:${params.VERSION}
            """

            bat "docker ps"

            echo "Candidate deployment started."
            echo "Old version is still running on port 8081."
        }
    }
}

        stage('Health Check and Automatic Rollback') {
    when {
        expression {
            params.DEPLOYMENT_ACTION == 'DEPLOY'
        }
    }
    steps {
        script {
            def candidateName = "retail-app-candidate"
            def containerName = "retail-app-uat"
            def networkName = "retail-network"
            def oldImage = env.OLD_IMAGE

            try {
                echo "Checking candidate application health..."
                echo "Candidate container: ${candidateName}"
                echo "Candidate port: 8082"

                bat """
                    powershell -Command "\$deadline=(Get-Date).AddSeconds(60); do { \$status=docker inspect --format='{{.State.Health.Status}}' ${candidateName}; Write-Host \\"Candidate health status: \$status\\"; if (\$status -eq 'healthy') { exit 0 }; if (\$status -eq 'unhealthy') { exit 1 }; Start-Sleep -Seconds 5 } while ((Get-Date) -lt \$deadline); exit 1"
                """

                echo "Candidate health check PASSED"

                echo "Candidate is healthy. Switching deployment..."

                bat """
                    docker rm -f ${containerName} >nul 2>&1 || exit /b 0
                """

                bat """
                    docker rm -f ${candidateName} >nul 2>&1 || exit /b 0
                """

                bat """
                    docker run -d ^
                    --name ${containerName} ^
                    --network ${networkName} ^
                    -p 8081:8081 ^
                    retail-app:${params.VERSION}
                """

                bat "docker ps"

                echo "New version is now running on production port 8081."
                echo "Deployed image: retail-app:${params.VERSION}"

            } catch (Exception e) {

                echo "========================================="
                echo "CANDIDATE HEALTH CHECK FAILED"
                echo "========================================="

                echo "Removing failed candidate..."

                bat """
                    docker rm -f ${candidateName} >nul 2>&1 || exit /b 0
                """

                if (!oldImage || oldImage == "NONE") {
                    error(
                        "Candidate health check failed and no previous image is available."
                    )
                }

                echo "Previous version remains available:"
                echo "${oldImage}"

                echo "========================================="
                echo "ROLLBACK / NO-SWITCH COMPLETED"
                echo "========================================="

                error(
                    "Candidate deployment failed. Old version was not removed."
                )
            }
        }
    }
}

        stage('Manual Rollback') {
            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'ROLLBACK'
                }
            }

            steps {
                script {
                    def containerName = "retail-app-uat"
                    def networkName = "retail-network"

                    echo "Starting manual rollback..."
                    echo "Rollback image: retail-app:${params.VERSION}"

                    bat """
                        docker network inspect ${networkName} >nul 2>&1 || docker network create ${networkName}
                    """

                    bat """
                        docker rm -f ${containerName} >nul 2>&1 || exit /b 0
                    """

                    bat """
                        docker run -d ^
                        --name ${containerName} ^
                        --network ${networkName} ^
                        -p 8081:8081 ^
                        retail-app:${params.VERSION}
                    """

                    bat "docker ps"

                    echo "Manual rollback container started."
                }
            }
        }

        stage('Manual Rollback Health Check') {
            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'ROLLBACK'
                }
            }

            steps {
                script {
                    def containerName = "retail-app-uat"

                    echo "Checking manual rollback health..."

                    bat """
                        powershell -Command "\$deadline=(Get-Date).AddSeconds(60); do { \$status=docker inspect --format='{{.State.Health.Status}}' ${containerName}; Write-Host \\"Rollback health status: \$status\\"; if (\$status -eq 'healthy') { exit 0 }; if (\$status -eq 'unhealthy') { exit 1 }; Start-Sleep -Seconds 5 } while ((Get-Date) -lt \$deadline); exit 1"
                    """

                    echo "Manual rollback health check PASSED"
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
            echo "Check whether automatic rollback was completed successfully."
        }
    }
}