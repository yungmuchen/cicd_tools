"""
This little script remove all .pyc files in the directory you specified.

Example:

    python rmpyc.py
    python rmpyc.py folder_1 folder_2
"""
import os, re, stat
def dirwalk(dir):
    "walk a directory tree, using a generator"
    for f in os.listdir(dir):
        fullpath = os.path.join(dir,f)
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for x in dirwalk(fullpath):  # recurse into subdir
                yield x
        else:
            yield fullpath

def rmpyc(fromdir='.'):
    hdr = "Remove pyc files in directory '%s'" % fromdir
    dsh = '-' * (len(hdr) + 2)
    print "\n+%s+\n| %s |\n+%s+" % (dsh, hdr, dsh)
    for x in dirwalk(fromdir):
        if re.match('.*\.pyc', x) and os.path.isfile(x):
            print 'DEL: [%s]' % x
            os.chmod(x, stat.S_IWRITE)
            os.remove(x)
        if re.match('.*~', x) and os.path.isfile(x):
            print 'DEL: [%s]' % x
            os.chmod(x, stat.S_IWRITE)
            os.remove(x)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for dir in sys.argv[1:]:
            rmpyc(dir)
    else:
        rmpyc()

