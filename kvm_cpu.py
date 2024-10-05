# coding: utf-8
import collectd
from discover_vm import discover


def config_cpu(data=None):
    collectd.debug("Configuration: " + repr(data))


def init_cpu(data=None):
    collectd.debug("Initialization: " + repr(data))



def get_total_cpu_time():
    """Get the total CPU time from /proc/stat."""
    with open("/proc/stat", "r") as f:
        line = f.readline()  # The first line contains the total CPU time
        fields = line.split()[1:]  # Skip the 'cpu' prefix
        return sum(int(field) for field in fields)  # Return the sum of all CPU time fields


def read_cpu(data=None):
    collectd.debug("Reading: " + repr(data))
    for pid, host in discover().items():
        # /var/lib/collectd/rrd/kvm_HOST/cpu_kvm/cpu-usage.rrd
        M = collectd.Values("gauge")  # Use gauge for CPU usage
        M.host = "kvm_" + host
        M.plugin = "cpu_kvm"

        # Separate user and system values
        with open("/proc/%s/stat" % pid, 'r') as f:
            stats = f.readline().split(' ')
            user, system = int(stats[13]), int(stats[14])
            user_wait, system_wait = int(stats[15]), int(stats[16])

        # Get total CPU time from /proc/stat
        total_cpu = get_total_cpu_time()

        M.type_instance = "cpu_user"
        M.values = [user]
        M.dispatch()

        M.type_instance = "cpu_system"
        M.values = [system]
        M.dispatch()

        M.type_instance = "cpu_total"
        M.values = [total_cpu]
        M.dispatch()

        M.type_instance = "cpu_wait"
        M.values = [user_wait + system_wait]
        M.dispatch()


# Register the configurations and reading callbacks for collectd
collectd.register_config(config_cpu)
collectd.register_init(init_cpu)
collectd.register_read(read_cpu)
