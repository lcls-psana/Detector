"""
:py:class:`EventCodeManager` class-helper for event selection using event code
==============================================================================

Usage::

    from Detector.EventCodeManager import EventCodeManager
    evcode = '1,2,4'
    ecm = EventCodeManager(evcode, verbos=0)
    for evt ds.events():
        if not ecm.select(evt): continue 

Methods:
  * :py:meth:`EventCodeManager.set_event_codes`
  * :py:meth:`EventCodeManager.select`

This software was developed for the LCLS project.
If you use all or part of it, please give an appropriate acknowledgment.

Created (moved from app/det_ndarr_raw_proc) on 2017-10-20 by Mikhail Dubrovin
"""
#from __future__ import print_function
#---

from Detector.EvrDetector import EvrDetector

class EventCodeManager(object):
    """Class-helper for event selection using event code.

    The string of comma-separated event codes is passed in evcode through option -c, (ex.: -c 1,2,4).
    If any of listed event codes are available in evt Evr event codes then method select(evt) returns True, otherwise False.
    If any of input event codes is set negative - then all event codes are used to deselect event.  
    More complicated logical formulaes are not supprorted.
    """
    def __init__(self, evcode=None, verbos=0):
        self.verbos = verbos
        self.set_event_codes(evcode)
        self.evrdet = EvrDetector(':Evr')
        self.do_check = self.lst_ec is not None and self.evrdet is not None
        if self.verbos & 1: print('%s: list of requested event codes: %s, do_check=%s' %\
           (self.__class__.__name__, str(self.lst_ec), self.do_check))
        self.counter = 0


    def set_event_codes(self, evcode):
        """Splits input (str) for list of integer event codes. Any negative event code inverts selection decision for all event codes."""

        if evcode is None or evcode.lower() == 'none':
            self.lst_ec = None
            return
        try:
            lst_ec = [int(field) for field in evcode.split(',')] # convert string to a list of int event codes
        except:
            self.lst_ec = None
            return
            
        self.do_deselect = any((ec<0 for ec in lst_ec))      # set do_deselect switch for any negative event code
        self.lst_ec = [abs(ec) for ec in lst_ec]             # list of unsigned integer event codes


    def event_codes(self, evt):
        """Returns list of event codes for evt."""
        return self.evrdet.eventCodes(evt)


    def event_code_list(self):
        """Returns list of event codes to select."""
        return self.lst_ec


    def select(self, evt):
        """Returns True/False to select/deselect event."""
        if not self.do_check: return True
        evt_codes = self.evrdet.eventCodes(evt)
        ec_in_event = any(ec in evt_codes for ec in self.lst_ec)
        res = (not ec_in_event) if self.do_deselect else ec_in_event
        if self.counter < 20:
            self.counter += 1
            if self.verbos & 2:
                print('%s.select: evt_codes=%s, result=%s' % (self.__class__.__name__, str(evt_codes), res))
                if self.counter == 20: print('%s.select: stop printing messages' % (self.__class__.__name__))
        return res

# EOF

