role = 'arn:aws:iam::084602632950:role/sagemaker-role'

import sagemaker as sage
from time import gmtime, strftime

sess = sage.Session()

print(sess)
