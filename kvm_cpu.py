# coding: utf-8
import collectd
import time
from discover_vm import discover


def config_cpu(data=None):
    collectd.debug("Configuration: " + repr(data))


def init_cpu(data=None):
    collectd.debug("Initialization: " + repr(data))

    def get_total_cpu_time():
        with open("/proc/stat", "r") as f:
            line = f.readline()
            fields = line.split()[1:]  # Skip the 'cpu' prefix
            return sum(int(field) for field in fields)

    # Get total CPU time at the start of the interval
    total_cpu_time_before = get_total_cpu_time()
    
    for pid, host in discover().items():
        # /var/lib/collectd/rrd/kvm_HOST/cpu_kvm/cpu-usage.rrd
        M = collectd.Values("derive")
        M.host = "kvm_" + host
        M.plugin = "cpu_kvm"
        M.type_instance = "cpu_usage"
        
        with open(f"/proc/{pid}/stat", 'r') as f:
            fields = f.readline().split(' ')
            user = int(fields[13])
            system = int(fields[14])
        
        cpu_used_before = user + system
        
        # Wait for the interval (e.g., 10 seconds)
        time.sleep(10)  # This would match your interval duration
        
        # Get total CPU time again after the interval
        total_cpu_time_after = get_total_cpu_time()
        
        # Get the updated CPU usage values
        with open(f"/proc/{pid}/stat", 'r') as f:
            fields = f.readline().split(' ')
            user = int(fields[13])
            system = int(fields[14])
        
        cpu_used_after = user + system
        
        # Calculate differences
        cpu_used_diff = cpu_used_after - cpu_used_before
        total_cpu_diff = total_cpu_time_after - total_cpu_time_before
        
        # Calculate CPU usage percentage
        if total_cpu_diff > 0:
            cpu_percentage = (cpu_used_diff / total_cpu_diff) * 100
        else:
            cpu_percentage = 0.0
        
        M.values = [cpu_percentage]
        M.dispatch()

# Register the configurations and reading callbacks for collectd
collectd.register_config(config_cpu)
collectd.register_init(init_cpu)
collectd.register_read(read_cpu)
