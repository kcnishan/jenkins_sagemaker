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

                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY_ID', credentialsId: 'AWS_CREDENTIALS', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]) {
                        // login to ECR - for now it seems that that the ECR Jenkins plugin is not performing the login as expected. I hope it will in the future.
                        sh("eval \$(aws ecr get-login --no-include-email | sed 's|https://||')")
                    }

                    // Push the Docker image to ECR
                    docker.withRegistry(ECRURL)
                    {
                        docker.image(IMAGE).push()
                    }
                }
                sh("pip install --user sagemaker")
                sh("pip install --user pathlib")

                sh("python container/sagemaker_runner.py")
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
