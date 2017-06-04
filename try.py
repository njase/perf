#!/usr/bin/env python3
import perf
import time
import argparse

def func():
    time.sleep(5)


#import sys
#import os
#sys.path.append(os.getcwd())
runner = perf.Runner()
myb = runner.bench_func('sleep', func)
myb.dump('exoutput.json',compact=False,replace=True)



#Bug1: myb.dump with replace=False fails
#Bug2: I cant set verbose mode if using API, runner.args is None, and attempt to add something causes failure at other places
#Bug3: tracemalloc collection should not happen for warmup. the location of code should be moved
#Bug4: Extension, can support for collection of external traces..provide general APIs
