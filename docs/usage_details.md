### Usage details
Let us assume that there is a MyApp application which you want to benchmark in some particular scenario.

A typical use case for such a benchmarking would be:

1. **Pre-setup** To ensure reliability of benchmark results, we need to do some steps manually. Refer to your respective HW guide or OS guide on how to disable them:
   1. Disable BIOS based performance boosting technologies
      1. CPU throttling/requency scaling techniques: e.g. Intel SpeedStep and AMD Cool'n'Quiet
      1. CPU thermal based performance boosting techniques: e.g. Intel TurboBoost and  AMD TurboCore
   1. Disable HyperTheading on Intel CPUs
   
1. **Get xtperf** Download [xtperf](https://github.com/njase/xtperf) and install it as:
   ```python
    $> python setup.py install
   ```
   this will be installed as module name "perf" 
      - Update any needed dependencies like matplotlib, statistics,psutil   

1. **Create benchmarking test scenario**
   Create a test.py (or any other name) and write small test code to trigger the "particular scenario" of MyApp.

   For useful analysis, benchmarking should always be performed for a controlled scenario.

   See [test.py](https://github.com/njase/xtperf/blob/master/try.py) for a simple example, and [ilastikbench](https://github.com/njase/ilastikbench/blob/master/ibench.py) for a real example of writing such a test.

   ***This test program is used as application process to collect process specific benchmark results***

1. **Run benchmarking**
   ```python
      $> python ibench.py --traceextstats 1 --loops=1 --values=1 -p 5 -o output.json
   ```
   Change -p <x> to the number of times  benchmarking should be performed, and -o <x>  as desired file name for output. The rest are recommended as such. See xtperf help for details.

1. **Analyze output or save for offline analysis**
   1. Graphical analysis of a single output with both system(-s) and process(-n) stats:
   ```python
      $> python -m perf plot -sn <mybenchmark.json>
   ```
   1. Graphical comparative analysis of two benchmark results with both system(-s) and process(-n) stats
   ```python
      $> python -m perf plot -sn <mybenchmark1.json> <mybenchmark.json>
   ```
   1. See results directly on command line:
   ```python
      $> python -m perf stats -x <mybenchmark.json>
      $> python -m perf dump -d <mybenchmark.json>
   ```

#### Output
The xtperf results can be stored in an output file in json format.

The results can be offline analyzed on command line using steps mentioned in previous section. These provide:
* Stats = mean, max and min in the collected benchmark results
* Dump = all the benchmark data

The results are displayed for each worker process and every periodic iteration within each worker.

They can also be offline analyzed graphically using steps mentioned in previous section. Sample output is shown below. 

These results show:
* Time benchmark on the top
* System wide benchmark on the left
* Process wide benchmark on the right

[System and Process benchmark](images/xtplot_combined_bm.png)

Other visualizations are possible, e.g. comparative plots across two benchmarks as shown below:
[System wide comparison](xtplot_comp_s.png)

[Process wide comparison](xtplot_comp_n.png)


### Remarks and recommendations
* For precision and accuracy reasons – run the experiment few times (3 times or more) to get reliable results
* For consistency of results, reboot the machine and repeat experiment
* Once steps 1,2,3 are performed on a machine, the regular benchmarking can be automated by writing scripts
* xtperf is based on [perf](https://github.com/haypo/perf) toolkit. Therefore, all the commands which are provided by [perf](https://github.com/haypo/perf) are supported by default. See perf help for more details