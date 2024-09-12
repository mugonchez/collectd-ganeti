# coding: utf-8
import collectd
from discover_vm import discover


def config_cpu_wait(data=None):
    collectd.debug("Configuration: " + repr(data))


def init_cpu_wait(data=None):
    collectd.debug("Initialization: " + repr(data))


def read_cpu_wait(data=None):
    collectd.debug("Reading: " + repr(data))
    for pid, host in discover().items():
        # /var/lib/collectd/rrd/kvm_HOST/cpu_kvm/cpu-wait.rrd
        M = collectd.Values("gauge")
        M.host = "kvm_" + host
        M.plugin = "cpu_kvm"
        M.type_instance = "cpu_wait"
        # Safely open the /proc/[pid]/stat file using a context manager
        with open(f"/proc/{pid}/stat", 'r') as f:
            fields = f.readline().split(' ')
            user = fields[15]
            system = fields[16]
        M.values = [int(user) + int(system)]
        M.dispatch()
