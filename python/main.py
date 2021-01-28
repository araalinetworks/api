#!/usr/bin/env python
"""
"""

from __future__ import print_function

__author__ = "Abhishek R. Singh <abhishek@araalinetworks.com>"
__date__ = "5 Jan 2020"
__version__ = "1.0"
__credits__ = "Guido van Rossum, for an excellent programming language."

import atexit
import getopt
import inspect
from io import StringIO
import os
import pydoc
import readline
import rlcompleter  # pylint: disable=W0611
import shlex
import subprocess
import sys
import traceback

readline.parse_and_bind("tab: complete")

try:
    raw_input = input
except NameError:
    pass

class ModGlobals:
    """
    Global variables used in this module
    """
    def __init__(self):
        self.verbose = 0
        self.slicing_interval = None
        self.progname = None

# globals
mod_globals = ModGlobals()  # pylint: disable=C0103


def eprint(*args, **kwargs):
    args = [a.decode() for a in args]
    print(*args, file=sys.stderr, **kwargs)


def run_command(command, result=False, strip=True, in_text=None, debug=False, env=os.environ):
    def collect_output(ret, output):
        if output:
            if strip:
                output = output.strip()
            if result:
                ret.append(output.decode())
            else:
                eprint(output)

    if debug:
    	print(command, result)
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                stderr=subprocess.PIPE,
    				env=env)
    ret = []
    if result:
        if in_text:
            outs, errs = process.communicate(input=in_text.encode())
        else:
            outs, errs = process.communicate()
        return process.poll(), outs+errs
    else:
        while True:
            rc = process.poll()
            err = process.stderr.readline() 
            out = process.stdout.readline()
            if rc is not None and not out and not err:
                return rc, "\n".join(ret)
            collect_output(ret, out)
            collect_output(ret, err)


def help(*args):  # pylint: disable=W0622
    """
    Provide auto-help on functions that have a help string and dont start
    with _ (underscore)
    """
    if len(args) == 0:
        all_functions = [x for x in sys.modules[__name__].__dict__.values() if
                         inspect.isfunction(x) and x.__name__ not in
                         ["main", "onecmd", "cli", "help"]
                         and not x.__name__.startswith("_")]
    else:
        all_functions = [x for x in sys.modules[__name__].__dict__.values() if
                         inspect.isfunction(x) and
                         [a for a in args if x.__name__.startswith(a)]]
    if 0:
        print([x.__name__ for x in all_functions])

    doc_strings = [(i.__name__, i.__doc__) for i in all_functions]
    doc_strings.sort(key=lambda x: x[0], reverse=0)
    # must have doc_string to get printed.
    doc_strings = ['  %-16s\t%s\n' % (i, j) for i, j in doc_strings if
                   j is not None]

    print("".join(doc_strings))
h = help  # pylint: disable=C0103


def onecmd(cmd):
    """
    Call a function based on cmd extraction. Also allows piping of commands.
    """
    if not cmd.strip():
        return
    if not cmd or cmd[0] == "#":
        return  # handle comments
    if cmd == "q":
        raise Usage("Come again, bye !!\n")

    # look for output modifiers
    cmd = cmd.split("|")

    # the main thing, without modifiers
    args = shlex.split(cmd[0])

    bak = sys.stdout
    sys.stdout = StringIO.StringIO()

    if 0:
        print(args[0])

    try:
        eval("%s%s" % (args[0], tuple(args[1:])))
    except Usage as err:
        if err.msg:
            print("***", err.msg)
    except:
        print(sys.exc_info())
        traceback.print_exc(file=sys.stderr)

    ostr = sys.stdout.getvalue()
    sys.stdout = bak

    debug = 0
    use_pager = 0
    if cmd[1:]:  # output modifier processing
        add_nl = 0
        for outmod in cmd[1:]:
            if debug:
                # pylint: disable=C0323
                eprint("processing OM", outmod)
            outmod = shlex.split(outmod)

            # this will make sure only last pager request will persist
            use_pager = 0
            if outmod[0].strip() in ["more", "less"]:
                use_pager = 1
            if debug:
                # pylint: disable=C0323
                eprint("pager:", use_pager, outmod[0].strip(), outmod)

            mypipe = subprocess.Popen(outmod, bufsize=0, stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
            ostr = mypipe.communicate(ostr)[0]
            add_nl = 1

        if add_nl:
            ostr += "\n"

    # use_pager = 1 # force paging, since there is always a flurry
    if use_pager:
        pydoc.pager(ostr)
    else:
        sys.stdout.write(ostr)

    if debug:
        # pylint: disable=C0323
        eprint("final output:", len(ostr))


def cli(prompt):
    """
    Provide a cli with a prompt to read user commands
    """
    while 1:
        try:
            instr = raw_input("%s> " % prompt).strip()
        except KeyboardInterrupt:
            continue

        onecmd(instr)


class Usage(Exception):
    """
    Exception class for this module. Used instead of sys.exit(n)
    """
    def __init__(self, msg=""):
        Exception.__init__(self, msg)
        self.msg = msg

    def __str__(self):
        return self.msg


def _usage():
    """
    Prints usage of this program
    """
    global mod_globals

    # pylint: disable=C0323
    eprint("Usage: " + mod_globals.progname + \
        " [-v <verbose>] <filename>")


def main(argv=None):
    """
    Argument parsing and main glue logic
    """
    global mod_globals

    try:
        if argv is None:
            argv = sys.argv

        mod_globals.progname = argv[0]
        prompt = mod_globals.progname.rsplit("/", 1)[-1].split(".", 1)[0]
        # main starts here

        try:
            optlist, args = getopt.getopt(argv[1:], 'v:')
        except getopt.GetoptError as cause:
            _usage()
            raise Usage(cause)

        # default values go here

        for opt in optlist:
            (option, value) = opt
            if option == "-v":
                mod_globals.verbose = int(value, 0)
            elif option == "-s":
                mod_globals.slicing_interval = int(value, 0)
            else:
                _usage()
                raise Usage("Unknown switch: %s %s" % (option, value))

        try:
            atexit.register(readline.write_history_file,
                            os.path.join(os.environ["HOME"],
                                         ".%s_history" % prompt))
            readline.read_history_file(os.path.join(os.environ["HOME"],
                                       ".%s_history" % prompt))
        except:  # pylint: disable=W0702
            if 0:
                print(sys.exc_info())
                traceback.print_exc(file=sys.stderr)

        if not args:
            cli(prompt)
        else:
            onecmd(" ".join(args))
        return 0

    except Usage as err:
        if err.msg:
            print("***", err.msg)
        return 1

if __name__ == '__main__':
    sys.exit(main())
