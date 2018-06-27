#!/usr/bin/python

import argparse
import subprocess
from subunit.v2 import StreamResultToBytes
import sys
import tempfile
from testrepository.testlist import parse_enumeration, parse_list, write_list


def write_enumeration(f, testids):
    stream = StreamResultToBytes(f)
    for testid in testids:
        stream.status(test_id=testid, test_status='exists')

parser = argparse.ArgumentParser(
    description="Test runner that supports both Python 2 and Python 3.")

parser.add_argument(
    "--load-list", metavar="PATH", help="Path to read list of tests to run from.",
    type=str)
parser.add_argument(
    "--list", help="List available tests.", action="store_true")

args = parser.parse_args()

if args.list:
    tests = []
    with subprocess.Popen(['python', './brz', 'selftest', '--subunit2', '--list'],
                         stdout=subprocess.PIPE).stdout as f:
        for n in parse_enumeration(f.read()):
            tests.append('python2.' + n)
    with subprocess.Popen(['python3', './brz', 'selftest', '--subunit2', '--list'],
                         stdout=subprocess.PIPE).stdout as f:
        for n in parse_enumeration(f.read()):
            tests.append('python3.' + n)
    write_enumeration(sys.stdout, tests)
else:
    if args.load_list:
        py2_tests = []
        py3_tests = []
        with open(args.load_list, 'r') as f:
            all_tests = parse_list(f.read())
        for testname in all_tests:
            if testname.startswith("python2."):
                py2_tests.append(testname[len('python2.'):].strip())
            elif testname.startswith("python3."):
                py3_tests.append(testname[len('python3.'):].strip())
            else:
                sys.stderr.write("unknown prefix %s\n" % testname)
        if py2_tests:
            with tempfile.NamedTemporaryFile() as py2f:
                write_list(py2f, py2_tests)
                py2f.flush()
                subprocess.call(
                    'python ./brz selftest --subunit2 --load-list=%s | subunit-filter -s --passthrough --rename "^" "python2."' % py2f.name, shell=True)

        if py3_tests:
            with tempfile.NamedTemporaryFile() as py3f:
                write_list(py3f, py3_tests)
                py3f.flush()
                subprocess.call(
                    'python ./brz selftest --subunit2 --load-list=%s | subunit-filter -s --passthrough --rename "^" "python3."' % py3f.name, shell=True)
    else:
        subprocess.call(
            'python ./brz selftest --subunit2 | subunit-filter -s --passthrough --rename "^" "python2."', shell=True)
        subprocess.call(
            'python ./brz selftest --subunit2 | subunit-filter -s --passthrough --rename "^" "python3."', shell=True)
