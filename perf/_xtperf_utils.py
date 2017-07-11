from perf._utils import (perf_get_extstats)
import matplotlib.pyplot as plt
import numpy as np
import datetime

def get_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

def line_plot(key,labels,values,splot):
    data = values[key]
    if isinstance(data[0],list):
        for i,item in enumerate(data):        
            x = np.arange(len(item)) + 1
            #@TODO: Hack for max 4 CPU plots to be displayes
            #To be fixed when req frozen
            if i < 4:
                splot.plot(x,item,'o-',label=labels[i])
    else:
        x = np.arange(len(data)) + 1
        splot.plot(x,data,'ko-')
        splot.fill_between(x,0,data,facecolor='#CC6666',interpolate=True,label=labels)
    splot.legend(loc=1)        

def stack_plot(key,labels,values,splot):
    colors = ['#CC6666','#1DACD6','#6E5160']
    data = values[key]
    if not isinstance(data[0],list):
        print("Error in input to stack_plot(), no list to stack")
        return

    first_item = True

    for i,item in enumerate(data):
        if first_item:
            first_item = False
            x = np.arange(len(item)) + 1
            splot.plot(x,item,'ko-')
            splot.fill_between(x,0,item,facecolor=colors[i%3],interpolate=True,label=labels[i])
            old_sum = item
        else:
            x = np.arange(len(item)) + 1
            new_sum = [round(a+b,2) for a,b in zip(item,old_sum)]       
            splot.plot(x,new_sum,'ko-')
            splot.fill_between(x,old_sum,new_sum,facecolor=colors[i%3],interpolate=True,label=labels[i])
            old_sum = new_sum
        splot.legend(loc=1)        

def plot_runtime(key,values,splot):
    line_plot(key,"bm time",values,splot)
    splot.set_ylabel('Time (sec)')
    splot.set_title("Benchmark time",position=(0.5,0.8),fontweight='bold')
    
def plot_cpu_load(key,values,splot):
    if key == "syscpuload":
        labels = ["CPU0","CPU1","CPU2","CPU3"]
        splot.set_title("Sys CPU load",position=(0.5,0.8),fontweight='bold')
    else:
        labels = ["CPU"]
        splot.set_title("Proc CPU load",position=(0.5,0.8),fontweight='bold')
    line_plot(key,labels,values,splot)
    splot.set_ylabel('Load Percentage')

def plot_cpu_util(key,values,splot):
    #I know the data is like [sys,user,(idle)]
    labels = ['system','user','idle']
    stack_plot(key,labels,values,splot)
    if key == "syscpuutil":
        splot.set_ylabel('Load Percentage')
        splot.set_title("Sys CPU utilization",position=(0.5,0.8),fontweight='bold')
    if key ==  "proccpuutil":
        splot.set_ylabel('Load time (sec)')
        splot.set_title("Proc CPU utilization",position=(0.5,0.8),fontweight='bold')

def plot_vm_util(key,values,splot):
    #I know the data is like [used,(free)]
    if key == "sysvm":
        labels = ['used','free']
        stack_plot(key,labels,values,splot)
        splot.set_title("Sys VM utilization",position=(0.5,0.8),fontweight='bold')
    if key == "procvm":
        labels = "used VM"
        line_plot(key,labels,values,splot)
        splot.set_title("Proc VM utilization",position=(0.5,0.8),fontweight='bold')
    splot.set_ylabel('VM Percentage')


def plot_single_bench(s,n,values):
    fig = plt.figure(figsize=(20, 12))

    nrows = 4
    if (s is True) and (n is True):
        ncols = 2
        scount = nrows*ncols - 1
        splot = [0]*scount
        #Runtime plot is separate from others
        splot[0] = fig.add_subplot(nrows,1,1)
        for i in range(1,scount):
            splot[i] = fig.add_subplot(nrows,ncols,i+2)
    else:
        ncols = 1
        scount = nrows*ncols
        splot = [0]*scount
        for i in range(scount):
            splot[i] = fig.add_subplot(nrows,ncols,i+1)

    if ncols == 1 and s is True:
        plot_runtime("runvalues",values,splot[0])
        plot_cpu_load("syscpuload",values,splot[1])
        plot_cpu_util("syscpuutil",values,splot[2])
        plot_vm_util("sysvm",values,splot[3])
        plt.tight_layout()
        filename = 'xtplot_s_'+get_timestamp()+'.png'
    elif ncols == 1 and n is True:
        plot_runtime("runvalues",values,splot[0])
        plot_cpu_load("procpuload",values,splot[1])
        plot_cpu_util("proccpuutil",values,splot[2])
        plot_vm_util("procvm",values,splot[3])
        plt.tight_layout()
        filename = 'xtplot_n_'+get_timestamp()+'.png'
    else:
        plot_runtime("runvalues",values,splot[0])
        plot_cpu_load("syscpuload",values,splot[1])
        plot_cpu_load("procpuload",values,splot[2])
        plot_cpu_util("syscpuutil",values,splot[3])
        plot_cpu_util("proccpuutil",values,splot[4])
        plot_vm_util("sysvm",values,splot[5])
        plot_vm_util("procvm",values,splot[6])
        plt.tight_layout()
        filename = 'xtplot_ns_'+get_timestamp()+'.png'
        
    fig.savefig(filename)
    print("Output file " + filename)


def plot_compare1(values1,values2):
    nrows = 4
    ncols = 2
    scount = nrows*ncols
    
    fig = plt.figure(figsize=(20, 12))
    splot = [0]*scount

    for i in range(scount):
        splot[i] = fig.add_subplot(nrows,ncols,i+1)

    plot_runtime("runvalues",values1,splot[0])
    plot_runtime("runvalues",values2,splot[1])
    plot_cpu_load("syscpuload",values1,splot[2])
    plot_cpu_load("syscpuload",values2,splot[3])
    plot_cpu_util("syscpuutil",values1,splot[4])
    plot_cpu_util("syscpuutil",values2,splot[5])
    plot_vm_util("sysvm",values1,splot[6])
    plot_vm_util("sysvm",values2,splot[7])
   
    plt.tight_layout()
    return fig

def plot_compare2(values1,values2):
    nrows = 4
    ncols = 2
    scount = nrows*ncols
    
    fig = plt.figure(figsize=(20, 12))
    splot = [0]*scount

    for i in range(scount):
        splot[i] = fig.add_subplot(nrows,ncols,i+1)

    plot_runtime("runvalues",values1,splot[0])
    plot_runtime("runvalues",values2,splot[1])
    plot_cpu_load("procpuload",values1,splot[2])
    plot_cpu_load("procpuload",values2,splot[3])
    plot_cpu_util("proccpuutil",values1,splot[4])
    plot_cpu_util("proccpuutil",values2,splot[5])
    plot_vm_util("procvm",values1,splot[6])
    plot_vm_util("procvm",values2,splot[7])
    
    plt.tight_layout()
    return fig

def plot_compare_bench(s,n,values1,values2):
    if (s is True) and (n is False):
        fig = plot_compare1(values1,values2)
        filename = 'xtplot_comp_s_'+get_timestamp()+'.png'
        fig.savefig(filename)
        print("Output file " + filename)
    elif (n is True) and (s is False):
        fig = plot_compare2(values1,values2)
        filename = 'xtplot_comp_n_'+get_timestamp()+'.png'
        fig.savefig(filename)
        print("Output file " + filename)
    else:
        fig1 = plot_compare1(values1,values2)
        fig2 = plot_compare2(values1,values2)
        filename = 'xtplot_comp_ns_sys_'+get_timestamp()+'.png'
        fig1.savefig(filename)
        print("Output file " + filename)
        filename = 'xtplot_comp_ns_proc_'+get_timestamp()+'.png'
        fig2.savefig(filename)
        print("Output file " + filename)
        

def make_plots(*args,**kwargs):
    s = kwargs["sys"]
    n = kwargs["proc"]
    comp = kwargs["compare_to"]

    if (s is False) and (n is False):
        print("Error in input to plot_fig, nothing to print")
        return

    if comp is False:
        plot_single_bench(s,n,args[0])
    else:
        plot_compare_bench(s,n,args[0],args[1])
        
def get_benchmark_values(bench,sys,proc):
    run_values = bench.get_values()
    run_values = [round(i,2) for i in run_values]
    bench_values = {"runvalues":run_values}

    ext_values = bench.get_extvalues()
    values = perf_get_extstats(ext_values,sys,proc)
    if values is not None:
        bench_values.update(values)

    return bench_values
 
def plot_benchmark(bench,sys=False,proc=False):
    values = get_benchmark_values(bench,sys,proc)
    make_plots(values,sys=sys,proc=proc,compare_to=False)

def plot_benchmark_comparison(bench1,bench2,sys=False,proc=False):
    values1 = get_benchmark_values(bench1,sys,proc)
    values2 = get_benchmark_values(bench2,sys,proc)
    make_plots(values1,values2,sys=sys,proc=proc,compare_to=True)
