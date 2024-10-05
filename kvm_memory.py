# coding: utf-8
import collectd
import os
import hashlib
from discover_vm import discover

def bytes_to_gb(bytes_value):
    return bytes_value / (2**30)

# Define md5_new using hashlib (works for both Python 2 and 3)
md5_new = hashlib.md5

def config_memory(data=None):
    # TODO: make configuration option to choose between quick (rough) and slow
    #       (exact) estimation
    collectd.debug("Configuration: " + repr(data))


PAGESIZE = 0


def init_memory(data=None):
    global PAGESIZE
    collectd.debug("Initialization: " + repr(data))
    # Set PAGESIZE in bytes
    PAGESIZE = os.sysconf("SC_PAGE_SIZE")



def read_memory(data=None):
    collectd.debug("Reading: " + repr(data))
    for pid, host in discover().items():
        # /var/lib/collectd/rrd/kvm_HOST/memory_kvm/memory-usage.rrd
        M = collectd.Values("bytes")
        M.host = "kvm_" + host
        M.plugin = "memory_kvm"
        M.type_instance = "memory_usage"

        if os.path.exists(f"/proc/{pid}/smaps"):
            # Slow but more accurate estimate
            digester = md5_new()
            shared, private, pss = 0, 0, 0

            # Open the smaps file in binary mode, and handle byte decoding
            with open(f"/proc/{pid}/smaps", "rb") as F:
                for line in F.readlines():
                    digester.update(line)
                    line = line.decode('ascii')  # Decode the line from bytes to string

                    if line.startswith("Shared"):
                        shared += int(line.split()[1])
                    elif line.startswith("Private"):
                        private += int(line.split()[1])
                    elif line.startswith("Pss"):
                        pss += 0.5 + float(line.split()[1])

            if pss > 0:
                shared = pss - private

            # Memory usage in bytes
            m_usage = 1024 * int(private + shared)
            M.values = [m_usage]

        else:
            # Rough but quick estimate
            with open(f"/proc/{pid}/statm", "rt") as statm:
                S = statm.readline().split()

            shared = int(S[2]) * PAGESIZE
            Rss = int(S[1]) * PAGESIZE
            private = Rss - shared
            m_usage = int(private) + int(shared)
            M.values = [m_usage]

        M.dispatch()

# Register the configuration, initialization, and read callbacks with collectd
collectd.register_config(config_memory)
collectd.register_init(init_memory)
collectd.register_read(read_memory)
