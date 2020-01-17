# role = 'arn:aws:iam::084602632950:role/sagemaker-role'
role = 'arn:aws:iam::084602632950:role/t2-edw-dev-sagemaker'
prefix = 'DEMO-scikit-byo-iris'
import sagemaker as sage
from pathlib import Path
print(Path(__file__).parent)

sess = sage.Session()


WORK_DIRECTORY = str(Path(__file__).parent.parent) + '/data'
data_location = sess.upload_data(WORK_DIRECTORY, key_prefix=prefix)

account = sess.boto_session.client('sts').get_caller_identity()['Account']
region = sess.boto_session.region_name
image = '{}.dkr.ecr.{}.amazonaws.com/sagemaker-decision-trees:latest'.format(account, region)

print(account)
print(region)
print(image)

tree = sage.estimator.Estimator(image,
                       role, 1, 'ml.c4.2xlarge',
                       output_path="s3://{}/output".format(sess.default_bucket()),
                       sagemaker_session=sess)

tree.fit(data_location, wait=False, logs="All")



