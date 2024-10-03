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

    total_cpu_time = get_total_cpu_time()
    
    for pid, host in discover().items():
        try:
            # Safely open the /proc/[pid]/stat file using a context manager
            with open(f"/proc/{pid}/stat", 'r') as f:
                fields = f.readline().split(' ')

                # Extract relevant CPU times for the specific process (user, system, and wait)
                user = int(fields[13])
                system = int(fields[14])
                io_wait = int(fields[16])
            
                if total_cpu_time == 0:
                    # Avoid division by zero if the total time is 0
                    continue

                # Calculate percentages for user, system, and io_wait times
                user_pct = (user / total_cpu_time) * 100
                system_pct = (system / total_cpu_time) * 100
                io_wait_pct = (io_wait / total_cpu_time) * 100

                # Dispatch CPU user time percentage
                M_user = collectd.Values(type="gauge")
                M_user.host = "kvm_" + host
                M_user.plugin = "cpu_kvm"
                M_user.type_instance = "cpu_user"
                M_user.values = [round(user_pct,4)]
                M_user.dispatch()

                # Dispatch CPU system time percentage
                M_system = collectd.Values(type="gauge")
                M_system.host = "kvm_" + host
                M_system.plugin = "cpu_kvm"
                M_system.type_instance = "cpu_system"
                M_system.values = [round(system_pct,4)]
                M_system.dispatch()

                # Dispatch CPU IO wait time percentage
                M_io_wait = collectd.Values(type="gauge")
                M_io_wait.host = "kvm_" + host
                M_io_wait.plugin = "cpu_kvm"
                M_io_wait.type_instance = "cpu_wait"
                M_io_wait.values = [round(io_wait_pct,4)]
                M_io_wait.dispatch()

        except Exception as e:
            collectd.error(f"Error reading CPU stats for PID {pid}: {e}")

# Register the configurations and reading callbacks for collectd
collectd.register_config(config_cpu)
collectd.register_init(init_cpu)
collectd.register_read(read_cpu)
