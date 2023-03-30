
"""
:py:class:`RepoManager`
=======================
Supports repository directories/files naming structure for app/deploy_constants

    dirrepo='/reg/g/psdm/detector/calib/constants/'
    <dirrepo>/[<dettype>]/logs/<year>/<time-stamp>_log_<script-name>_<uid>.txt
          ex: logs/2022/2022-04-15T084054_log_deploy_constants_dubrovin.txt
    <dirrepo>/<dettype>/
    <dirrepo>/epix100a/
    <dirrepo>/<dettype>/.aliases.txt
		        default/<default-files>
		            ex: epix100a_default_gain.data # filled with 0.06 keV/ADO
		            ex: epix100a_default_common_mode.data # (4,6,30,10)
		        panels/<panel-id-or-detname>/<calib-type>/<constants>.data

    /reg/g/psdm/logs/atstart/2022/2022_lcls1_deploy_constants.txt


Usage::

    import Detector.RepoManager as rm
    # args - namespace of arguments,
    # all args are optional and default values should work in general case.
    args.dirrepo = './work'  # can be used for debugging and not spoiling real repository
    repoman = rm.init_repoman_and_logger(args)
    # do work, when dettype (ex. 'epix100a') is available call
        repoman.set/dir/makedir_dettype(dettype)
    # at the very end, before exit call
    repoman.logfile_save()


This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Re-factored from Detector.UtilsCalib class RepoManager on 2022-06-03 by Mikhail Dubrovin
"""

import logging
logger = logging.getLogger(__name__)

import os
from time import time, strftime, localtime
import PSCalib.GlobalUtils as cgu
from Detector.dir_root import DIR_REPO, DIR_LOG_AT_START

log_rec_at_start, create_directory, save_textfile, change_file_ownership =\
  cgu.log_rec_at_start, cgu.create_directory, cgu.save_textfile, cgu.change_file_ownership
TSTAMP_FORMAT = '%Y%m%d%H%M%S'


def str_tstamp(fmt='%Y-%m-%dT%H:%M:%S', time_sec=None):
    """Returns string timestamp for specified format and time in sec or current time by default
    """
    return strftime(fmt, localtime(time_sec))


class RepoManager():
    """Supports repository directories/files naming structure for app/deploy_constants.
    """

    def __init__(self, dirrepo, **kwa):
        self.dirrepo = dirrepo.rstrip('/')
        self.dirmode     = kwa.get('dirmode',  0o2777)
        self.dettype     = kwa.get('dettype', None)
        self.filemode    = kwa.get('filemode', 0o666)
        self.umask       = kwa.get('umask', 0o0)
        self.group       = kwa.get('group', 'ps-users')
        self.year        = kwa.get('year', str_tstamp(fmt='%Y'))
        self.tstamp      = kwa.get('tstamp', str_tstamp(fmt='%Y-%m-%dT%H%M%S'))
        self.dir_log_at_start = kwa.get('dir_log_at_start', DIR_LOG_AT_START)
        self.logsuffix   = kwa.get('logsuffix', 'nondef')
        self.dirname_log = kwa.get('dirname_log', 'logs')
        self.dirname_def = kwa.get('dirname_def', 'default')
        #self.dirname_pan = kwa.get('dirname_pan', 'panels')
        self.logname_tmp = None  # logname before the dettype is defined


    def makedir(self, d):
        """create and return directory d with mode defined in object property
        """
        create_directory(d, mode=self.dirmode, group=self.group)
        if not os.path.exists(d): logger.error('NOT CREATED DIRECTORY %s' % d)
        return d


    def dir_in_repo(self, name):
        """return directory <dirrepo>/<name>
        """
        return os.path.join(self.dirrepo, name)


    def makedir_in_repo(self, name):
        """create and return directory <dirrepo>/<name>
        """
        d = self.makedir(self.dirrepo)
        return self.makedir(self.dir_in_repo(name))


    def set_dettype(self, dettype):
        if dettype is not None:
            self.dettype = dettype


    def dir_dettype(self, dettype=None):
        """returns path to the dettype directory like <dirrepo>/[<dettype>]
        """
        self.set_dettype(dettype)
        return self.dirrepo if self.dettype is None else\
               os.path.join(self.dirrepo, self.dettype)


    def makedir_dettype(self, dettype=None):
        """create and returns path to the director type directory like <dirrepo>/[<dettype>]
        """
        d = self.makedir(self.dirrepo)
        ddt = self.dir_dettype(dettype)
        return d if self.dettype is None else\
               self.makedir(ddt)


    def dir_logs(self):
        """return directory <dirrepo>/[dettype]/logs
        """
        d = self.dir_dettype()
        return os.path.join(d, self.dirname_log)
        #return self.dir_in_repo(self.dirname_log)


    def makedir_logs(self):
        """create and return directory <dirrepo>/[dettype]/logs
        """
        #d = self.makedir(self.dirrepo)
        d = self.makedir_dettype()
        return self.makedir(self.dir_logs())


    def dir_logs_year(self, year=None):
        """return directory <dirrepo>/[dettype]/logs/<year>
        """
        _year = str_tstamp(fmt='%Y') if year is None else year
        return os.path.join(self.dir_logs(), _year)


    def makedir_logs_year(self, year=None):
        """create and return directory <dirrepo>/[dettype]/logs/<year>
        """
        d = self.makedir_logs()
        return self.makedir(self.dir_logs_year(year))


    def fname_aliases(self, dettype=None, fname='.aliases.txt'):
        d = self.makedir_dettype(dettype)
        return os.path.join(d, fname)


    def dir_default(self, dettype=None):
        """returns path to panel directory like <dirrepo>/<dettype>/<dirname_def>
        """
        return os.path.join(self.dir_dettype(dettype), self.dirname_def)


    def makedir_default(self, dettype=None):
        """create and returns path to panel directory like <dirrepo>/<dettype>/<dirname_def>
        """
        d = self.makedir_dettype(dettype)
        dp = self.makedir(self.dir_default())
        logger.info('default directory: %s' % dp)
        return dp


    def fname_default(self, dettype, ctype):
        return '%s/%s_default_%s.txt' % (self.dir_default(dettype), dettype, ctype)


    def dir_panel(self, panel_id):
        """returns path to panel directory like <dirrepo>/<dettype>/<panel_id>
        """
        return os.path.join(self.dir_dettype(), panel_id)


    def makedir_panel(self, panel_id):
        """create and returns path to panel directory like <dirrepo>/<dettype>/<panel_id>
        """
        d = self.makedir_dettype()
        dp = self.makedir(self.dir_panel(panel_id))
        logger.info('panel directory: %s' % dp)
        return dp


    def dir_ctype(self, panel_id, ctype): # ctype='pedestals'
        """returns path to the directory like <dirrepo>/<dettype>/<panel_id>/<ctype>
        """
        return '%s/%s' % (self.dir_panel(panel_id), ctype)


    def makedir_ctype(self, panel_id, ctype): # ctype='pedestals'
        """create and returns path to the directory like <dirrepo>/<dettype>/<panel_id>/<ctype>
        """
        d = self.makedir_panel(panel_id)
        return self.makedir(self.dir_ctype(panel_id, ctype))


    def dir_ctypes(self, panel_id, ctypes=('gain', 'common_mode', 'geometry')):
        """define structure of subdirectories in calibration repository under <dirrepo>/<panel_id>/...
           subdirs=('pedestals', 'rms', 'status', 'plots')
        """
        return ['%s/%s'%(self.dir_panel(panel_id), name) for name in ctypes]


    def makedir_ctypes(self, panel_id, ctypes=('gain', 'common_mode', 'geometry')):
        """create structure of subdirectories in calibration repository under <dirrepo>/<panel_id>/...
        """
        dp = self.makedir_panel(panel_id)
        dirs = self.dir_ctypes(panel_id, ctypes=ctypes)
        for d in dirs: self.makedir(d)
        return dirs


    def logname(self, logsuffix=None):
        if logsuffix is not None: self.logsuffix = logsuffix
        tstamp = str_tstamp(fmt='%Y-%m-%dT%H%M%S')
        s = '%s/%s_log_%s.txt' % (self.makedir_logs_year(), tstamp, self.logsuffix)
        if self.logname_tmp is None:
           self.logname_tmp = s
        return s

    ### lcls2 style of logname_at_start_lcls1: DIR_LOG_AT_START/<year>/<year>_lcls1_<procname>.txt

    def logname_at_start(self, suffix, year=None):
        _year = str_tstamp(fmt='%Y') if year is None else str(year)
        return '%s/%s_log_%s.txt' % (self.makedir_logs(), _year, suffix)


    def dir_log_at_start_year(self):
        """return directory <dirlog_at_start>/<year>"""
        return os.path.join(self.dir_log_at_start, self.year)


    def makedir_log_at_start_year(self):
        """create and return directory"""
        return self.makedir(self.dir_log_at_start_year())


    def logname_at_start_lcls1(self, procname):
        return '%s/%s_lcls1_%s.txt' % (self.makedir_log_at_start_year(), self.year, procname)


    def save_record_at_start(self, procname, tsfmt='%Y-%m-%dT%H:%M:%S', adddict={}):
        os.umask(self.umask)
        d = {'dirrepo':self.dirrepo,}
        if adddict: d.update(adddict)
        rec = log_rec_at_start(tsfmt, **d)
        logfname = self.logname_at_start_lcls1(procname)
        fexists = os.path.exists(logfname)
        save_textfile(rec, logfname, mode='a')
        if not fexists:
            os.chmod(logfname, self.filemode)
            change_file_ownership(logfname, user=None, group=self.group)
        logger.info('record at start: %s\nsaved in: %s' % (rec, logfname))


    def logfile_save(self):
        """The final call to repo-manager which
           - moves originally created logfile under the dettype directory,
           - change its access mode and group ownershp.
        """
        logname = self.logname() # may be different from logname_tmp after definition of dettype
        if logname != self.logname_tmp:
            cmd = 'mv %s %s' % (self.logname_tmp, logname)
            logger.info('move logfile under dettype:\n%s' % '\n    '.join(cmd.split()))
            os.system(cmd)
            cmd = 'ln -s %s %s' % (logname, self.logname_tmp)
            logger.info('create link to logfile')
            os.system(cmd)

        os.chmod(logname, self.filemode)
        cgu.change_file_ownership(logname, user=None, group=self.group)


def init_repoman_and_logger(args):
    """wrapper for common pattern of initialization RepoManager and logger
    """
    import getpass
    from Detector.UtilsLogging import sys, init_logger

    scrname   = sys.argv[0].split('/')[-1]

    dirrepo   = getattr(args, 'dirrepo', DIR_REPO)
    logmode   = getattr(args, 'logmode', 'INFO')
    logsuffix = getattr(args, 'logsuffix', '%s_%s' % (scrname, getpass.getuser()))
    group     = getattr(args, 'group', 'ps-users')
    filemode  = getattr(args, 'filemode', 0o664)
    dirmode   = getattr(args, 'dirmode', 0o2775)
    fmt       = getattr(args, 'fmt', '[%(levelname).1s] %(filename)s L%(lineno)04d %(message)s')
    dir_log_at_start = getattr(args, 'dir_log_at_start', DIR_LOG_AT_START)

    if 'work' in args.dirrepo: dir_log_at_start = args.dirrepo
    repoman = RepoManager(dirrepo, dir_log_at_start=dir_log_at_start,\
                          dirmode=dirmode, filemode=filemode, group=group, logsuffix=logsuffix)
    logname = repoman.logname()
    init_logger(loglevel=logmode, logfname=logname, group=group, fmt=fmt)
    logger.info('log file: %s' % logname)
    repoman.save_record_at_start(scrname, adddict={'logfile':logname})
    return repoman

# EOF
