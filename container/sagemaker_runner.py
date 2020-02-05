# role = 'arn:aws:iam::084602632950:role/sagemaker-role'
role = 'arn:aws:iam::084602632950:role/t2-edw-dev-sagemaker'
prefix = 'DEMO-scikit-byo-iris'
bucket = 't2-edw-dev-sagemaker'
project = 'sagemaker-decision-trees'
import sagemaker as sage
from pathlib import Path
from sagemaker.session import Session
import time
#import boto3

print(Path(__file__).parent)
import sys

sess = sage.Session(default_bucket=bucket)


print(sess.default_bucket())

WORK_DIRECTORY = str(Path(__file__).parent.parent) + '/data'

data_path = "{}/{}/{}".format(project, sys.argv[2], sys.argv[1])
data_location = sess.upload_data(bucket=bucket, path=WORK_DIRECTORY, key_prefix=data_path)

print(data_location)
account = sess.boto_session.client('sts').get_caller_identity()['Account']
region = sess.boto_session.region_name
image = '{}.dkr.ecr.{}.amazonaws.com/{}:latest'.format(account, region, project)

print(account)
print(region)
print(image)

print(sys.argv)

model_output_path = "s3://{}/{}/{}/{}".format(bucket, project, sys.argv[2], sys.argv[1])
# transformer_output_path = "s3://{}/{}/{}/{}".format


job_name = "{}-{}".format(sys.argv[2], sys.argv[1])

training_params = {
    "RoleArn": role,
    "TrainingJobName": job_name,
    "AlgorithmSpecification": {
        "TrainingImage": image,
        "TrainingInputMode": "File",
        "MetricDefinitions": [
            {
                "Name": "train:error",
                "Regex": "Train_error=(.*?);"
            },
            {
                "Name": "validation:error",
                "Regex": "Valid_error=(.*?);"
            }]
    },
    "ResourceConfig": {
        "InstanceCount": 1,
        "InstanceType": 'ml.c4.2xlarge',
        "VolumeSizeInGB": 2
    },
    "InputDataConfig": [
        {
            "ChannelName": "training",
            "DataSource": {
                "S3DataSource": {
                    "S3DataType": "S3Prefix",
                    "S3Uri": data_location,
                    "S3DataDistributionType": "FullyReplicated"
                }
            },
            "CompressionType": "None",
            "RecordWrapperType": "None"
        }
    ],
    "OutputDataConfig": {
        "S3OutputPath": model_output_path
    },
    "StoppingCondition": {
        "MaxRuntimeInSeconds": 60 * 60
    }
}


sm_session = Session()
sm = sm_session.boto_session.client('sagemaker')
sm.create_training_job(**training_params)

status = sm.describe_training_job(TrainingJobName=job_name)['TrainingJobStatus']
print(status)
sm_session.logs_for_job(job_name=job_name, wait=True)
sm.get_waiter('training_job_completed_or_stopped').wait(TrainingJobName=job_name)
status = sm.describe_training_job(TrainingJobName=job_name)['TrainingJobStatus']
print("Training job ended with status: " + status)
if status == 'Failed':
    message = sm.describe_training_job(TrainingJobName=job_name)['FailureReason']
    print('Training failed with the following error: {}'.format(message))
    raise Exception('Training job failed')




model_name = job_name + '-mod'

info = sm.describe_training_job(TrainingJobName=job_name)
model_data = info['ModelArtifacts']['S3ModelArtifacts']
print(model_data)

primary_container = {
    'Image': image,
    'ModelDataUrl': model_data
}

create_model_response = sm.create_model(
    ModelName = model_name,
    ExecutionRoleArn = role,
    PrimaryContainer = primary_container)

print(create_model_response['ModelArn'])



batch_job_name = job_name + '-transform'
transform_request = \
{
    "TransformJobName": batch_job_name,
    "ModelName": model_name,
    "BatchStrategy": "MultiRecord",
    "TransformOutput": {
        "S3OutputPath": model_output_path
    },
    "TransformInput": {
        "DataSource": {
            "S3DataSource": {
                "S3DataType": "S3Prefix",
                "S3Uri": data_location
            }
        },
        "ContentType": "text/csv",
        "SplitType": "Line",
        "CompressionType": "None",
        "InputFilter": "$[1:]"
    },
    "TransformResources": {
            "InstanceType": "ml.m4.xlarge",
            "InstanceCount": 1
    }
}



sm.create_transform_job(**transform_request)

while (True):
    response = sm.describe_transform_job(TransformJobName=batch_job_name)
    status = response['TransformJobStatus']
    if status == 'Completed':
        print("Transform job ended with status: " + status)
        break
    if status == 'Failed':
        message = response['FailureReason']
        print('Transform failed with the following error: {}'.format(message))
        raise Exception('Transform job failed')
    print("Transform job is still in status: " + status)
    time.sleep(30)

# sm = sess
# sm.create_training_job(**training_params)
#
# status = sm.describe_training_job(TrainingJobName=job_name)['TrainingJobStatus']
# print(status)
# sm_session.logs_for_job(job_name=pipe_job, wait=True)
# sm.get_waiter('training_job_completed_or_stopped').wait(TrainingJobName=job_name)
# status = sm.describe_training_job(TrainingJobName=job_name)['TrainingJobStatus']
# print("Training job ended with status: " + status)
# if status == 'Failed':
#     message = sm.describe_training_job(TrainingJobName=job_name)['FailureReason']
#     print('Training failed with the following error: {}'.format(message))
#     raise Exception('Training job failed')

# tree = sage.estimator.Estimator(image,
#                                 role, 1, 'ml.c4.2xlarge',
#                                 output_path=model_output_path,
#                                 sagemaker_session=sess,
#                                 enable_sagemaker_metrics=True,
#                                 metric_definitions=[
#                                     {'Name': 'train:error', 'Regex': 'Train_error=(.*?);'},
#                                     {'Name': 'validation:error', 'Regex': 'Valid_error=(.*?);'}
#                                 ]
#                                 )
#
#
# print(data_location)
# tree.fit(data_location + '/iris.csv', wait=True, logs="All")
#
# print('start transformer')
#
# transform_output_folder = "batch-transform-output"
#
# transformer = tree.transformer(instance_count=1,
#                                instance_type='ml.m4.xlarge',
#                                output_path=model_output_path,
#                                assemble_with='Line',
#                                accept='text/csv')
#
# transformer.transform(data_location + '/iris.csv', content_type='text/csv', split_type='Line', input_filter='$[1:]')
# transformer.wait()
