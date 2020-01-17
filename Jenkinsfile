pipeline
{
    agent { label 'linux' }
    environment
    {
        IMAGE = 'sagemaker-decision-trees'
        ECRURL = 'https://084602632950.dkr.ecr.us-west-2.amazonaws.com/sagemaker-decision-trees'
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
                    
                    sh("wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate")
                    sh("python get-pip.py --user")
                    sh('export PATH=$PATH:/home/jenkins/.local/bin')
                    sh('export PATH=$PATH:/home/jenkins/.local/bin; pip install --user --upgrade setuptools')
                    sh("export PATH=$PATH:/home/jenkins/.local/bin; pip install --user awscli")

                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY_ID', credentialsId: 'AWS_CREDENTIALS', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]) {
                        // login to ECR - for now it seems that that the ECR Jenkins plugin is not performing the login as expected. I hope it will in the future.
                        sh("export PATH=$PATH:/home/jenkins/.local/bin; aws configure set region us-west-2")
                        sh("export PATH=$PATH:/home/jenkins/.local/bin; eval \$(aws ecr get-login --no-include-email | sed 's|https://||')")

                        docker.withRegistry(ECRURL)
                        {
                            docker.image(IMAGE).push()
                        }


                        sh("export PATH=$PATH:/home/jenkins/.local/bin; pip install --user sagemaker")
                        sh("export PATH=$PATH:/home/jenkins/.local/bin; pip install --user pathlib")
                        sh("export PATH=$PATH:/home/jenkins/.local/bin;python container/sagemaker_runner.py")
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
