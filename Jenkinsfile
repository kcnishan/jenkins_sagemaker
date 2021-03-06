pipeline
{

    agent { label 'linux' }
    environment
    {
        IMAGE = 't2-entapps-edw-dev-sagemaker-decision-trees'
        ECRURL = 'https://317631987873.dkr.ecr.us-west-2.amazonaws.com/t2-entapps-edw-dev-sagemaker-decision-trees'
        ECRCRED = 'AWS'


    }
    stages
    {

        stage('Docker build')
        {
            steps
            {
                script
                {
                    // Build the docker image using a Dockerfile
                    docker.build("$IMAGE", 'container')
                }
            }
        }
        stage('Docker push')
        {
            steps
            {
                script

                {

                    final scmVars = checkout(scm)
                    echo "scmVars: ${scmVars}"
                    echo "scmVars: ${scmVars.GIT_BRANCH}"
                    echo "scmVars: ${scmVars.GIT_COMMIT}"

                    shortCommit = sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
                    echo shortCommit

                    sh("wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate")
                    sh("python get-pip.py --user")
                    sh('export PATH=$PATH:/home/jenkins/.local/bin')
                    sh('export PATH=$PATH:/home/jenkins/.local/bin; pip install --user --upgrade setuptools')
                    sh("export PATH=$PATH:/home/jenkins/.local/bin; pip install --user awscli")

                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY_ID', credentialsId: 'AWS_CREDENTIALS', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]) {
                        // login to ECR - for now it seems that that the ECR Jenkins plugin is not performing the login as expected. I hope it will in the future.
                         echo AWS_ACCESS_KEY_ID
                         echo AWS_SECRET_ACCESS_KEY

                        sh("export PATH=$PATH:/home/jenkins/.local/bin; aws configure set region us-west-2")
                        sh("export PATH=$PATH:/home/jenkins/.local/bin; eval \$(aws ecr get-login --no-include-email | sed 's|https://||')")

                        docker.withRegistry(ECRURL)
                        {
                            docker.image(IMAGE).push()
                        }

                        sh("export PATH=$PATH:/home/jenkins/.local/bin; pip install --user pandas")
                        sh("export PATH=$PATH:/home/jenkins/.local/bin; pip install --user sagemaker")
                        sh("export PATH=$PATH:/home/jenkins/.local/bin; pip install --user pathlib")
                        sh("export PATH=$PATH:/home/jenkins/.local/bin;python container/sagemaker_runner.py ${scmVars.GIT_COMMIT} ${scmVars.GIT_BRANCH}")

                    }

                    // Push the Docker image to ECR
                }

            }
        }
    }

    post
    {
        always
        {
            // make sure that the Docker image is removed
            sh "docker rmi $IMAGE | true"
        }
    }
}
