from perf._utils import (perf_get_extstats)



def plot_benchmark(bench,sys=False,proc=False):
    run_values = {"runvalues":bench.get_values()}

    ext_values = bench.get_extvalues()
    values = perf_get_extstats(ext_values,sys,proc)
    values.update(run_values)

    print("Plot is based on")
    print(values)
    #https://matplotlib.org/examples/pylab_examples/fill_between_demo.html

def plot_benchmark_comparison(bench1,bench2,sys=False,proc=False):
    pass
