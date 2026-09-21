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

                    /*
                     * Check whether the current container exists.
                     */
                    def containerExists = bat(
                        script: "docker inspect ${containerName} >nul 2>&1",
                        returnStatus: true
                    )

                    def oldImage = "NONE"

                    /*
                     * If the container exists, get its image.
                     */
                    if (containerExists == 0) {
                        oldImage = bat(
                            script: "docker inspect --format=\"{{.Config.Image}}\" ${containerName}",
                            returnStdout: true
                        ).trim()

                        echo "Docker inspect returned: ${oldImage}"
                    }

                    if (!oldImage || oldImage == "") {
                        oldImage = "NONE"
                    }

                    echo "Previous UAT image: ${oldImage}"
                    echo "New image: retail-app:${params.VERSION}"

                    /*
                     * Store previous image for rollback.
                     */
                    env.OLD_IMAGE = oldImage

                    echo "Container: ${containerName}"
                    echo "Network: ${networkName}"
                    echo "Host port: 8081"

                    /*
                     * Make sure network exists.
                     */
                    bat "docker network inspect ${networkName} >nul 2>&1 || docker network create ${networkName}"

                    /*
                     * Remove current container.
                     */
                    bat "docker rm -f ${containerName} >nul 2>&1 || exit /b 0"

                    /*
                     * Start requested version.
                     */
                    bat """
                        docker run -d ^
                        --name ${containerName} ^
                        --network ${networkName} ^
                        -p 8081:8081 ^
                        retail-app:${params.VERSION}
                    """

                    bat "docker ps"

                    echo "Deployment started successfully."
                    echo "Previous image: ${oldImage}"
                    echo "Current image : retail-app:${params.VERSION}"
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
                    def containerName = "retail-app-uat"
                    def networkName = "retail-network"
                    def oldImage = env.OLD_IMAGE

                    try {

                        echo "Waiting for application health check..."

                        bat """
                            powershell -Command "\$deadline=(Get-Date).AddSeconds(60); do { \$status=docker inspect --format='{{.State.Health.Status}}' ${containerName}; Write-Host \\"Health status: \$status\\"; if (\$status -eq 'healthy') { exit 0 }; if (\$status -eq 'unhealthy') { exit 1 }; Start-Sleep -Seconds 5 } while ((Get-Date) -lt \$deadline); exit 1"
                        """

                        echo "Application health check PASSED"

                    } catch (Exception e) {

                        echo "========================================="
                        echo "HEALTH CHECK FAILED"
                        echo "========================================="

                        if (!oldImage || oldImage == "NONE") {
                            error(
                                "Health check failed, but no previous Docker image is available for rollback."
                            )
                        }

                        echo "Starting automatic rollback..."
                        echo "Rollback image: ${oldImage}"

                        /*
                         * Remove failed version.
                         */
                        bat "docker rm -f ${containerName} >nul 2>&1 || exit /b 0"

                        /*
                         * Restore previous image.
                         */
                        bat """
                            docker run -d ^
                            --name ${containerName} ^
                            --network ${networkName} ^
                            -p 8081:8081 ^
                            ${oldImage}
                        """

                        bat "docker ps"

                        echo "Previous version started: ${oldImage}"
                        echo "Waiting for rollback health check..."

                        /*
                         * Validate restored version.
                         */
                        bat """
                            powershell -Command "\$deadline=(Get-Date).AddSeconds(60); do { \$status=docker inspect --format='{{.State.Health.Status}}' ${containerName}; Write-Host \\"Rollback health status: \$status\\"; if (\$status -eq 'healthy') { exit 0 }; if (\$status -eq 'unhealthy') { exit 1 }; Start-Sleep -Seconds 5 } while ((Get-Date) -lt \$deadline); exit 1"
                        """

                        echo "========================================="
                        echo "ROLLBACK SUCCESSFUL"
                        echo "Restored image: ${oldImage}"
                        echo "========================================="

                        /*
                         * Rollback succeeded, but deployment failed.
                         * Therefore Jenkins must finish as FAILURE.
                         */
                        error(
                            "Deployment failed. Automatic rollback completed successfully."
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