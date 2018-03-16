#!/usr/bin/python

#
# Utility to extract OpenCV cmake options
#

import argparse
import collections
import fnmatch
import os
import re


def findfiles(path, pat):
    res = []
    if isinstance(pat, list):
        pat_list = pat
    else:
        pat_list = [pat]
    for pat in pat_list:
        pat_dir = os.path.dirname(pat)
        pat_file = os.path.basename(pat)
        for root, dirs, fnames in os.walk(os.path.join(path, pat_dir)):
            for fname in fnames:
                if fnmatch.fnmatch(fname, pat_file):
                    res.append(os.path.join(root, fname))
    return res


def grep(filepath, regex):
    robj = re.compile(regex)
    res = []
    with open(filepath) as f:
        for line in f:
            mobj = robj.match(line)
            if mobj:
                groups = mobj.groups()
                if len(groups) == 1:
                    res.append(groups[0])
                else:
                    res.append(groups)
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir")
    args = parser.parse_args()

    # files = findfiles(args.source_dir, ["CMakeLists.txt", "cmake/*.cmake"])
    # opts = []
    # for file in files:
    #     for opt in grep(file, r"^\s*OCV_OPTION\((\S+)"):
    #         if not opt in opts:  # probably not needed
    #             opts.append(opt)

    cache = os.path.join(args.build_dir, "CMakeCache.txt")
    opts_cache = collections.OrderedDict()
    for (name, typ) in grep(cache, r"^(\w+):(\w+)="):
        opts_cache[name] = typ

    # for opt in opts:
    #     if opt in opts_cache:
    #         print("\"{0}\": \"{1}\",".format(opt.lower(), opts_cache[opt]))
    #     else:
    #         print("\"{0}\"".format(opt.lower()))

    for name in opts_cache:
        typ = opts_cache[name]
        bool_opt = \
            name.startswith("WITH") or \
            name.startswith("BUILD") or \
            name.startswith("ENABLE")
        other_opt = \
            name.startswith("INSTALL") or \
            name.startswith("OPENCV")
        if typ != "INTERNAL" and typ != "STATIC":
            if typ.endswith("PATH"):
                typ = "STRING"
            elif typ == "UNINITIALIZED" and bool_opt:
                typ = "BOOL"
            if bool_opt or other_opt:
                print("(\"{0}\", \"{1}\"),".format(name.lower(), typ.lower()))
