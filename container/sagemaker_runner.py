# role = 'arn:aws:iam::084602632950:role/sagemaker-role'
role = 'arn:aws:iam::084602632950:role/t2-edw-dev-sagemaker'
prefix = 'DEMO-scikit-byo-iris'
bucket = 't2-edw-dev-sagemaker'
project = 'sagemaker-decision-trees'
import sagemaker as sage
from pathlib import Path

print(Path(__file__).parent)
import sys


sess = sage.Session(default_bucket=bucket)

print(sess.default_bucket())

WORK_DIRECTORY = str(Path(__file__).parent.parent) + '/data'

#key_prefix = "{}".format(project)
data_location = sess.upload_data(bucket=bucket, path=WORK_DIRECTORY, key_prefix=project)



account = sess.boto_session.client('sts').get_caller_identity()['Account']
region = sess.boto_session.region_name
image = '{}.dkr.ecr.{}.amazonaws.com/{}:latest'.format(account, region, project)

print(account)
print(region)
print(image)

print(sys.argv)

model_output_path = "s3://{}/{}/{}/{}/".format(bucket, project, sys.argv[2], sys.argv[1])

tree = sage.estimator.Estimator(image,
                                role, 1, 'ml.c4.2xlarge',
                                output_path=model_output_path,
                                sagemaker_session=sess,
                                enable_sagemaker_metrics=True,
                                metric_definitions=[
                                    {'Name': 'train:error', 'Regex': 'Train_error=(.*?);'},
                                    {'Name': 'validation:error', 'Regex': 'Valid_error=(.*?);'}
                                ]
                                )


print(data_location)
tree.fit(data_location + '/iris.csv', wait=True, logs="All")

print('start transformer')

transform_output_folder = "batch-transform-output"

transformer = tree.transformer(instance_count=1,
                               instance_type='ml.m4.xlarge',
                               output_path=model_output_path,
                               assemble_with='Line',
                               accept='text/csv')

transformer.transform(data_location + '/iris.csv', content_type='text/csv', split_type='Line', input_filter='$[1:]')
transformer.wait()
