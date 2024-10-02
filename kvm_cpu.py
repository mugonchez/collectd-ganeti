# coding: utf-8
import collectd
from discover_vm import discover


def config_cpu(data=None):
    collectd.debug("Configuration: " + repr(data))


def init_cpu(data=None):
    collectd.debug("Initialization: " + repr(data))


def read_cpu(data=None):
    collectd.debug("Reading: " + repr(data))
    for pid, host in discover().items():
        # /var/lib/collectd/rrd/kvm_HOST/cpu_kvm/cpu-usage.rrd
        M = collectd.Values("derive")  # or try "counter"
        M.host = "kvm_" + host
        M.plugin = "cpu_kvm"
        M.type_instance = "cpu_usage"
        # Safely open the /proc/[pid]/stat file using a context manager
        with open(f"/proc/{pid}/stat", 'r') as f:
            fields = f.readline().split(' ')
            user = fields[13]
            system = fields[14]
        M.values = [int(user) + int(system)]
        M.dispatch()


# Register the configurations and reading callbacks for collectd
collectd.register_config(config_cpu)
collectd.register_init(init_cpu)
collectd.register_read(read_cpu)
