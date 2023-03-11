"""define DIR_ROOT for repositories and logfiles through the environment variable:
   /reg/g/psdm # lcls
   /cds/group/psdm # lcls2
   /sdf/group/lcls/ds/ana/  # on s3df etc.
"""
import os

DIR_ROOT = os.getenv('SIT_ROOT')
DIR_REPO = os.path.join(DIR_ROOT, 'detector/calib/constants/')
DIR_LOG_AT_START = os.path.join(DIR_ROOT, 'detector/logs/atstart/')
DIR_REPO_STATUS = os.path.join(DIR_ROOT, 'detector/calib/constants/status/')

DIR_PSDM_DATA = os.getenv('SIT_PSDM_DATA')
DIR_ROOT_DATA = DIR_PSDM_DATA # '/reg/d/psdm'  # dcs
# EOF
