"""define DIR_ROOT for repositories and logfiles through the environment variable:
   /reg/g/psdm # lcls
   /cds/group/psdm # lcls2
   /sdf/g/psdm  # on s3df etc.
"""
import os

DIR_ROOT = os.getenv('SIT_ROOT')  # /reg/g/psdm
DIR_REPO = os.path.join(DIR_ROOT, 'detector/calib/constants/')
DIR_LOG_AT_START = os.path.join(DIR_ROOT, 'logs/atstart/')

DIR_ROOT_DATA = '/reg/d/psdm'  # dcs

# EOF
