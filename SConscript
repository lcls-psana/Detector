#--------------------------------------
#  SConscript file for package Detector
#--------------------------------------

# Do not delete following line, it must be present in
# SConscript file for any SIT project
Import('*')

#
# For the standard SIT packages which build libraries, applications,
# and Python modules it is usually sufficient to call
# standardSConscript() function which defines rules for all
# above targets. Many standard packages do not need any special options,
# but those which need can modify standardSConscript() behavior using
# a number of arguments, here is a complete list:
#
#    LIBS - list of additional libraries needed by this package
#    LIBPATH - list of directories for additional libraries
#    BINS - dictionary of executables and their corresponding source files
#    TESTS - dictionary of test applications and their corresponding source files
#    SCRIPTS - list of scripts in app/ directory
#    UTESTS - names of the unit tests to run, if not given then all tests are unit tests
#    PYEXTMOD - name of the Python extension module, package name used by default
#    CCFLAGS - additional flags passed to C/C++ compilers
#    NEED_QT - set to True to enable Qt support
#
#standardSConscript()
#standardSConscript(PYEXTMOD="detector_ext", DOCGEN="doxy-all pyana-ref", CCFLAGS="-std=gnu++11")
standardSConscript(UTESTS=['unittest_detector', 'test_unittest_sample'], PYEXTMOD="detector_ext", DOCGEN="doxy-all pyana-ref", CCFLAGS="-std=gnu++11")

# EOF
