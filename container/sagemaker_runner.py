role = 'arn:aws:iam::084602632950:role/sagemaker-role'

import sagemaker as sage
from time import gmtime, strftime

sess = sage.Session()

account = sess.boto_session.client('sts').get_caller_identity()['Account']
region = sess.boto_session.region_name
image = '{}.dkr.ecr.{}.amazonaws.com/sagemaker-decision-trees:latest'.format(account, region)

print(account)
print(region)
print(image)

