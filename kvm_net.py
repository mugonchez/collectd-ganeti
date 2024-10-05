# coding: utf-8
import collectd
from discover_vm import discover, discover_nic

def bytes_to_mb(bytes_value):
    return bytes_value / (2**20)


def config_net(data=None):
    collectd.debug("Configuration: " + repr(data))


def init_net(data=None):
    collectd.debug("Initialization: " + repr(data))

def read_net(data=None):
    collectd.debug("Reading: " + repr(data))
    for pid, host in discover().items():
        nics = discover_nic(host)
        if len(nics) < 1:
            continue

        # /var/lib/collectd/rrd/kvm_HOST/net_kvm/net-{in,out}.rrd
        M_in = collectd.Values("counter")
        M_in.host = "kvm_" + host
        M_in.plugin = "net_kvm"
        M_in.type_instance = "net_in"
        M_out = collectd.Values("counter")
        M_out.host = "kvm_" + host
        M_out.plugin = "net_kvm"
        M_out.type_instance = "net_out"

        # Open the file using a context manager to ensure safe file handling
        with open("/proc/net/dev", "r") as f:
            for line in f:
                if nics[0] in line:
                    # Split and clean the line to extract the needed values
                    s = line.strip().split()[1:]  # Skip the interface name and take the rest

                    # Assign the parsed values to M_in and M_out
                    M_in.values = [int(s[0])]   # Receive bytes
                    M_out.values = [int(s[8])]  # Transmit bytes
                    break  # Break after processing the relevant line

        # Dispatch the values to collectd
        M_in.dispatch()
        M_out.dispatch()

# Register the configuration, initialization, and read callbacks with collectd
collectd.register_config(config_net)
collectd.register_init(init_net)
collectd.register_read(read_net)
