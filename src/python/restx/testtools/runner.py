
import sys
import datetime

import restx.core
from restx.testtools.utils import init_test_run

def _get_func( func_name ):
    """
    Return a function object for a function specified by name.

    This function is courtesy of hasen j, who supplied it as an
    answer to this StackOverflow question:

        http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname

    """
    parts = func_name.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def _make_timediff_str(start_time, end_time):
    """
    Return properly formatted string with difference in start and end time (datetime.datetime object).

    """
    td = end_time - start_time
    return "%d.%06d" % (td.seconds, (td.microseconds * 1000000) / 1000000)

overall_start_time = datetime.datetime.now()
overall_fail_count = 0
overall_test_count = 0

modnames    = sys.argv[1:]
failed_list = list()
for name in modnames:
    # Patch the name: Remove .py at the end and replace '/' with '.'
    orig_name = name
    if name.endswith(".py"):
        name = name[:-3]
    if name.startswith("./"):
        name = name[2:]
    module_name = name.replace("/", ".")
    runfunc = _get_func(module_name+".runtest")
    start_time = datetime.datetime.now()
    print "---------------------------------------------------------------------"
    print "--- Running runtest() from file: ", orig_name
    print "---"
    init_test_run()
    num_failed, num_total = runfunc()
    end_time = datetime.datetime.now()
    overall_fail_count += num_failed
    overall_test_count += num_total
    print "---"
    if num_failed == 0:
        print "--- Ok."
    else:
        print "--- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    Failed %d out of %d tests!" % (num_failed, num_total)
        failed_list.append( ( orig_name, num_failed ) )
    print "--- Total elapsed time: ", _make_timediff_str(start_time, end_time)
    print "---------------------------------------------------------------------\n"

overall_end_time = datetime.datetime.now()

print "====================================================================="
print ("=== Ran %d tests: " % overall_test_count),
if overall_fail_count == 0:
    print "Ok."
else:
    print "%d failed." % overall_fail_count
print "=== Overall elapsed time: ", _make_timediff_str(overall_start_time, overall_end_time)

if failed_list:
    print "==="
    print "=== Error summary:"
    for name, num in failed_list:
        print "===   %3d failed tests in: %s" % (num, name)
print "=====================================================================\n"



