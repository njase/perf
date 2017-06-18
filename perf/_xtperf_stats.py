from multiprocessing import Process, Queue
import time
import psutil
from os import getpid
import numpy as np

def collect_stats(ppid,childq,tts):
    p = psutil.Process(ppid)
    collector = XPerfStats()
    while(1):
        stats = collector.read_raw_stats(p)
        childq.put(stats)
        print("Sleeping for " + str(tts) + "seconds")
        time.sleep(tts)



#Open a new process and start stat collection periodically
class XPerfStatsTask:
    def __init__(self,sampling_rate_sec):
        self._sleep = sampling_rate_sec
        self._pid = getpid()
        self._q = Queue(10)
        self._p = Process(target=collect_stats, args=(self._pid,self._q,self._sleep))

    def start(self):
        self._p.start()
        ##Temporarily added a sleep to allow atleast one data collection
        #print("Remove this temp sleep")
        #time.sleep(4)

    def stop(self):
        self._p.terminate()
        tmp = []
        while not self._q.empty():
            tmp.append(self._q.get())
     
        #Pass this list to XPerfStats object asking it to give back formatted dictionary object 
        stats = XPerfStats().format_raw_stats(tmp)
        return stats


class XPerfStats():
    def __init__(self,extstats=None):
        self.valid = False

    #Utility function to collect stats
    def read_raw_stats(self,phdl):
        sys_cpu_per = psutil.cpu_percent(interval=1,percpu=True)
 
        cput = psutil.cpu_times()
        total_time = sum(cput)
        sys_cpu_times = [round((cput.user/total_time)*100,2),
                         round((cput.system/total_time)*100,2),
                         round((cput.idle/total_time)*100,2)]

        vm = psutil.virtual_memory()
        sys_vm_data = [vm.percent, 100.0-vm.percent]


        #Process specific collection
        pp_cpu_per = phdl.cpu_percent(interval=1)

        pcput = phdl.cpu_times()
        pp_cpu_times = [pcput.user,pcput.system]

        pp_vm_data = round(phdl.memory_percent(),2)
        
        csw = phdl.num_ctx_switches()
        pp_ctx_switches = [csw.voluntary,csw.involuntary]

        return [sys_cpu_per,sys_cpu_times,sys_vm_data,pp_cpu_per,pp_cpu_times,pp_vm_data,pp_ctx_switches]

    #utility function to make a dictionary from list of stats
    def format_raw_stats(self,extstats):
        dict_data = {}
        dict_data["Sys_CPU%"] = []
        dict_data["Sys_user_time%"] = []
        dict_data["Sys_system_time%"] = []
        dict_data["Sys_idle_time%"] = []
        dict_data["Sys_used_VM%"] = []
        dict_data["Sys_available_VM%"] = []
        dict_data["Proc_CPU%"] = []
        dict_data["Proc_user_time_sec"] = []
        dict_data["Proc_system_time_sec"] = []
        dict_data["Proc_used_VM%"] = []
        dict_data["Proc_vol_ctx_switch"] = []
        dict_data["Proc_invol_ctx_switch"] = []

        for data in extstats:
            dict_data["Sys_CPU%"].append(data[0])
            dict_data["Sys_user_time%"].append(data[1][0])
            dict_data["Sys_system_time%"].append(data[1][1])
            dict_data["Sys_idle_time%"].append(data[1][2])
            dict_data["Sys_used_VM%"].append(data[2][0])
            dict_data["Sys_available_VM%"].append(data[2][1])
            dict_data["Proc_CPU%"].append(data[3])
            dict_data["Proc_user_time_sec"].append(data[4][0])
            dict_data["Proc_system_time_sec"].append(data[4][1])
            dict_data["Proc_used_VM%"].append(data[5])
            dict_data["Proc_vol_ctx_switch"].append(data[6][0])
            dict_data["Proc_invol_ctx_switch"].append(data[6][1])

        return dict_data


    #Read a dictionary and save lists of different stats
    def parse_formatted_stats(self,extstats):
        #Input is unfortunately compilcated..simlify it a bit
        #Make a new list of dictionaries
        nvalues = len(extstats)
        if nvalues == 0:
            self.valid = False
            return
        else:
            self.valid = True

        raw_stats = []
        for data in extstats:
            raw_stats.append(data[0][0])

        ###############
        self._ncores = len(raw_stats[0]["Sys_CPU%"][0])

        first = 12*[True]
        for data in raw_stats:
             for cpu_data in data["Sys_CPU%"]:
                 if first[0]:
                     self.cpu_load_np_arr = np.array([cpu_data])
                     first[0] = False
                 else:
                     self.cpu_load_np_arr = np.append(self.cpu_load_np_arr,[cpu_data] ,axis=0)

             for cpu_data in data["Proc_CPU%"]:
                 if first[1]:
                     self.cpu_proc_load_np_arr = np.array([cpu_data])
                     first[1] = False
                 else:
                     self.cpu_proc_load_np_arr = np.append(self.cpu_proc_load_np_arr,[cpu_data])
         
             for cpu_data in data["Sys_user_time%"]:
                 if first[2]:
                    self.cpu_user_util_np_arr = np.array([cpu_data])
                    first[2] = False
                 else:
                    self.cpu_user_util_np_arr = np.append(self.cpu_user_util_np_arr,[cpu_data])

             for cpu_data in data["Sys_system_time%"]:
                 if first[3]:
                    self.cpu_sys_util_np_arr = np.array([cpu_data])
                    first[3] = False
                 else:
                    self.cpu_sys_util_np_arr = np.append(self.cpu_sys_util_np_arr,[cpu_data])

             for cpu_data in data["Sys_idle_time%"]:
                 if first[4]:
                    self.cpu_idle_util_np_arr = np.array([cpu_data])
                    first[4] = False
                 else:
                    self.cpu_idle_util_np_arr = np.append(self.cpu_idle_util_np_arr,[cpu_data])

             for cpu_data in data["Proc_user_time_sec"]:
                 if first[5]:
                    self.cpu_proc_user_util_np_arr = np.array([cpu_data])
                    first[5] = False
                 else:
                    self.cpu_proc_user_util_np_arr = np.append(self.cpu_proc_user_util_np_arr,[cpu_data])

             for cpu_data in data["Proc_system_time_sec"]:
                 if first[6]:
                    self.cpu_proc_sys_util_np_arr = np.array([cpu_data])
                    first[6] = False
                 else:
                    self.cpu_proc_sys_util_np_arr = np.append(self.cpu_proc_sys_util_np_arr,[cpu_data])

             for vm_data in data["Sys_used_VM%"]:
                 if first[7]:
                    self.sys_used_vm_np_arr = np.array([vm_data])
                    first[7] = False
                 else:
                    self.sys_used_vm_np_arr = np.append(self.sys_used_vm_np_arr,[vm_data])

             for vm_data in data["Sys_available_VM%"]:
                 if first[8]:
                    self.sys_free_vm_np_arr = np.array([vm_data])
                    first[8] = False
                 else:
                    self.sys_free_vm_np_arr = np.append(self.sys_free_vm_np_arr,[vm_data])

             for vm_data in data["Proc_used_VM%"]:
                 if first[9]:
                    self.proc_used_vm_np_arr = np.array([vm_data])
                    first[9] = False
                 else:
                    self.proc_used_vm_np_arr = np.append(self.proc_used_vm_np_arr,[vm_data])

             for ctx_data in data["Proc_vol_ctx_switch"]:
                 if first[10]:
                    self.proc_vol_ctx_np_arr = np.array([ctx_data])
                    first[10] = False
                 else:
                    self.proc_vol_ctx_np_arr = np.append(self.proc_vol_ctx_np_arr,[ctx_data])

             for ctx_data in data["Proc_invol_ctx_switch"]:
                 if first[11]:
                    self.proc_invol_ctx_np_arr = np.array([ctx_data])
                    first[11] = False
                 else:
                    self.proc_invol_ctx_np_arr = np.append(self.proc_invol_ctx_np_arr,[ctx_data])

    def xperf_stat(self):
        lines = []
        if not self.valid:
            lines.append("-------------------")
            lines.append("No external data available to display!!")
            lines.append("-------------------")
            return lines

        lines.append("\nSystem wide external stats:-")
        lines.append("CPU core binding - TBD ")
    
        ############
        lines.append("CPU loading in %:")
        tmp = "             C0"
        for i in range(self._ncores-1):
            tmp = tmp + "   C" + str(i+1) + " "
        lines.append(tmp)

        tmp = "   max      " + str(np.max(self.cpu_load_np_arr,axis=0))
        lines.append(tmp)
        tmp = "   min      " + str(np.min(self.cpu_load_np_arr,axis=0))
        lines.append(tmp)
        ############
    

        ############
        lines.append("\n CPU utilization in %:")
        lines.append("            User    Sys    Idle")
        tmp = "   max      " + str(np.max(self.cpu_user_util_np_arr)) + "    " + str(np.max(self.cpu_sys_util_np_arr)) + "    " + str(np.max(self.cpu_idle_util_np_arr))
        lines.append(tmp)
        tmp = "   min      " + str(np.min(self.cpu_user_util_np_arr)) + "    " + str(np.min(self.cpu_sys_util_np_arr)) + "    " + str(np.min(self.cpu_idle_util_np_arr))
        lines.append(tmp)
        ############
    
    
        ############
        lines.append("\n Virtual memory utilization in %:")
        lines.append("            Used    Available")
        tmp = "   max      " + str(np.max(self.sys_used_vm_np_arr)) + "    " + str(np.max(self.sys_free_vm_np_arr))
        lines.append(tmp)
        tmp = "   min      " + str(np.min(self.sys_used_vm_np_arr)) + "    " + str(np.min(self.sys_free_vm_np_arr))
        lines.append(tmp)
        ############

        lines.append("\nProcess specific external stats :-")
        ############
        lines.append("CPU loading in %:")
        tmp = "   max      " + str(np.max(self.cpu_proc_load_np_arr,axis=0))
        lines.append(tmp)
        tmp = "   min      " + str(np.min(self.cpu_proc_load_np_arr,axis=0))
        lines.append(tmp)
        ############
 
        ############
        lines.append("\n CPU utilization in sec:")
        lines.append("            User    Sys")
        tmp = "   max      " + str(np.max(self.cpu_proc_user_util_np_arr)) + "    " + str(np.max(self.cpu_proc_sys_util_np_arr)) 
        lines.append(tmp)
        tmp = "   min      " + str(np.min(self.cpu_proc_user_util_np_arr)) + "    " + str(np.min(self.cpu_proc_sys_util_np_arr))
        lines.append(tmp)
        ############

        ############
        lines.append("\n Context switch count:")
        lines.append("            Vol    Invol")
        tmp = "   max      " + str(np.max(self.proc_vol_ctx_np_arr)) + "    " + str(np.max(self.proc_invol_ctx_np_arr)) 
        lines.append(tmp)
        tmp = "   min      " + str(np.min(self.proc_vol_ctx_np_arr)) + "    " + str(np.min(self.proc_invol_ctx_np_arr)) 
        lines.append(tmp)
        ############

        ############
        lines.append("\n Virtual memory utilization in %:")
        lines.append("            Used")
        tmp = "   max      " + str(np.max(self.proc_used_vm_np_arr))
        lines.append(tmp)
        tmp = "   min      " + str(np.min(self.proc_used_vm_np_arr))
        lines.append(tmp)
        ############
        return lines

    def xperf_dump(self):
        lines = []
        if not self.valid:
            lines.append("-------------------")
            lines.append("No external data available to display!!")
            lines.append("-------------------")
            return lines

        lines.append("- System wide external stats:")
    
        ############
        lines.append("    - CPU loading in % :")
        tmp = "     C0"
        for i in range(self._ncores-1):
            tmp = tmp + "   C" + str(i+1) + " "
        lines.append(tmp)
        for i in self.cpu_load_np_arr:
            lines.append("    " + str(i))

        ############
        lines.append("    - CPU utilization in %")
        lines.append("    User    Sys    Idle")
        cnt = len(self.cpu_user_util_np_arr)
        for i in range(cnt):
            lines.append("    " + str(self.cpu_user_util_np_arr[i]) +
                         "    " + str(self.cpu_sys_util_np_arr[i]) +
                         "    " + str(self.cpu_idle_util_np_arr[i]))
        ############
    
        ############
        lines.append("    - Virtual memory utilization in %")
        lines.append("     Used    Available")
        cnt = len(self.sys_used_vm_np_arr)
        for i in range(cnt):
            lines.append("    " + str(self.sys_used_vm_np_arr[i]) +
                         "    " + str(self.sys_free_vm_np_arr[i]))
        ############
        lines.append("- Process wide external stats:")
    
        ############
        lines.append("    - CPU loading in % :")
        for i in self.cpu_proc_load_np_arr:
            lines.append("    " + str(i))

        lines.append("    - CPU utilization in sec")
        lines.append("    User    Sys")
        cnt = len(self.cpu_proc_user_util_np_arr)
        for i in range(cnt):
            lines.append("    " + str(self.cpu_proc_user_util_np_arr[i]) +
                         "    " + str(self.cpu_proc_sys_util_np_arr[i]))
        
        lines.append("    - Context switch count")
        lines.append("    Vol    Invol")
        cnt = len(self.proc_vol_ctx_np_arr)
        for i in range(cnt):
            lines.append("    " + str(self.proc_vol_ctx_np_arr[i]) +
                         "    " + str(self.proc_invol_ctx_np_arr[i]))

        lines.append("    - Virtual memory utilization in %")
        lines.append("    Used")
        cnt = len(self.proc_used_vm_np_arr)
        for i in range(cnt):
            lines.append("    " + str(self.proc_used_vm_np_arr[i]))
        ############
        return lines

    def xperf_get_values(self,sys=False,proc=False):
        values = {}

        if (not self.valid) or (sys is False and proc is False):
            print("No external data available to display!!")
            return values

        if sys is True:
            values["ncores"] = self._ncores
            values["syscpuload"] = []
            for i in range(self._ncores):
                cpu_arr = self.cpu_load_np_arr[:,i]
                values["syscpuload"].append(cpu_arr.tolist());

            values["syscpuutil"] = [] #sys,user,idle
            cpu_arr = self.cpu_sys_util_np_arr 
            values["syscpuutil"].append(cpu_arr.tolist())
            cpu_arr = self.cpu_user_util_np_arr
            values["syscpuutil"].append(cpu_arr.tolist())
            cpu_arr = self.cpu_idle_util_np_arr
            values["syscpuutil"].append(cpu_arr.tolist())

            values["sysvm"] = [] #used, available  
            vm_arr = self.sys_used_vm_np_arr
            values["sysvm"].append(vm_arr.tolist())
            vm_arr = self.sys_free_vm_np_arr
            values["sysvm"].append(vm_arr.tolist())
  
        if proc is True:
            values["procpuload"] = []
            cpu_arr = self.cpu_proc_load_np_arr
            values["procpuload"].append(cpu_arr.tolist())

            values["proccpuutil"] = []
            cpu_arr = self.cpu_proc_sys_util_np_arr
            values["proccpuutil"].append(cpu_arr.tolist())
            cpu_arr = self.cpu_proc_user_util_np_arr
            values["proccpuutil"].append(cpu_arr.tolist())

            vm_arr = self.proc_used_vm_np_arr
            values["procvm"] = vm_arr.tolist()

            values["procctx"] = [] #Voluntary, involuntary
            cpu_arr = self.proc_vol_ctx_np_arr
            values["procctx"].append(cpu_arr.tolist())
            cpu_arr = self.proc_invol_ctx_np_arr
            values["procctx"].append(cpu_arr.tolist())

           
        return values
