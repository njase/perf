# xtperf

*Credits: xtperf is a derivative work of [perf](https://github.com/haypo/perf) module*

#### What is xtperf
xtperf is a generic tool which provides support to collect and analyze several types of real-time benchmarking information for python applications. 
These include :
* time benchmarking
* CPU throughput
* CPU utilization
* VM utilization

These are collected both for the complete system as well as for the application process. 
The data can be analyzed and compared offline by xtperf commands.

xtperf has been written to allow analysis of large multi-threaded applications on multicore CPUs.
It is best supported on Desktop Linux.

#### What is a benchmark?
A benchmark is a particular test run in a controlled environment whose results can be counted as a metric on performance. 
Depending on application, several different types of KPI can be covered in the benchmark result, broadly covered under - time and throughput KPIs. 
The benchmark specifies the units of that metric, and whether less is better or not.

#### Benefits:
*  to assess how the differential changes, software parameters, design choices, system settings and/or platform differences impact the overall execution time 
*  Guide investigation for profiling


#### Setup and Usage
For usage details, follow [this](usage_details.md) link.

Note that xtperf is based on [perf](https://github.com/haypo/perf) toolkit. Therefore, all the commands which are provided by perf are supported by default!

#### How it works
Explanation is TBD. For now, see the source code or ask me for any questions.

*xtperf is distributed under the MIT license*

