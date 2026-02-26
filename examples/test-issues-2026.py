#!/usr/bin/env python
"""
USAGE: <python> Detector/examples/test-issues-2026.py 1
"""
from Detector.UtilsLogging import sys, logging, STR_LEVEL_NAMES, basic_config
logger = logging.getLogger(__name__)
SCRNAME = sys.argv[0].rsplit('/')[-1]


def issue_2026_01_20():
    """ISSUE: https://jira.slac.stanford.edu/browse/ECS-9567
       REASON: simultaneous requests to create directory?
       FIXED: see gu.create_directory - add try-exception
       ./Detector/examples/test-issues-2026.py 1 -L DEBUG
    """
    import PSCalib.GlobalUtils as gu
    kwa={}
    gu.create_directory('./2026-test-dir', mode=0o2775, group='ps-users', **kwa)


def issue_2026_MM_DD():
    """ISSUE:
       REASON:
       FIXED:
    """
    metname = sys._getframe().f_code.co_name
    print('method: %s' % metname)
    print('docstring:', eval(metname).__doc__)


def argument_parser():
    from argparse import ArgumentParser
    d_tname   = '0'
    d_dsname  = 'exp=xpplw3319:run=293'  # None
    d_detname = 'epix_alc3'  # None
    d_logmode = 'INFO' # 'DEBUG'  # 'INFO'
    d_addpar  = None
    h_tname   = 'test name, usually numeric number, default = %s' % d_tname
    h_dsname  = 'dataset name, default = %s' % d_dsname
    h_detname = 'input ndarray source name, default = %s' % d_detname
    h_logmode = 'logging mode, one of %s, default = %s' % (STR_LEVEL_NAMES, d_logmode)
    h_addpar  = 'additional parameter, default = %s' % d_addpar
    parser = ArgumentParser(description='%s is a bunch of tests for annual issues' % SCRNAME, usage=USAGE())
    parser.add_argument('tname',            default=d_tname,    type=str,   help=h_tname)
    parser.add_argument('-d', '--dsname',   default=d_dsname,   type=str,   help=h_dsname)
    parser.add_argument('-s', '--detname',  default=d_detname,  type=str,   help=h_detname)
    parser.add_argument('-L', '--logmode',  default=d_logmode,  type=str,   help=h_logmode)
    parser.add_argument('-a', '--addpar',   default=d_addpar,   type=str,   help=h_addpar)
    return parser


def USAGE():
    import inspect
    return '\n  %s <TNAME>\n' % sys.argv[0].split('/')[-1]\
    + '\n'.join([s for s in inspect.getsource(selector).split('\n') if "TNAME in" in s])


def selector():
    parser = argument_parser()
    args = parser.parse_args()
    basic_config(format='[%(levelname).1s] L%(lineno)04d: %(filename)s %(message)s', int_loglevel=None, str_loglevel=args.logmode)
    logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING) # get rid of messages

    TNAME = args.tname  # sys.argv[1] if len(sys.argv)>1 else '0'
    if   TNAME in  ('1',): issue_2026_01_20() # strarup time is 15sec?
    elif TNAME in  ('2',): issue_2026_01_20() # time to access constants

    else:
        print(USAGE())
        sys.exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

    sys.exit('END OF TEST %s'%TNAME)


if __name__ == "__main__":
    selector()
# EOF
