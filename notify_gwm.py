# coding: utf-8
from urllib.parse import urlencode
from urllib.request import urlopen
import collectd

GWM_HOST = None  # This will still be set by configuration but isn't checked.


def warning(msg):
    collectd.warning("[notify-gwm] %s" % msg)


def log_data(data):
    # Log the data before sending it
    collectd.info("[notify-gwm] Sending notification data: %s" % data)


def init_notify_gwm(data=None):
    collectd.debug("Initialization: " + repr(data))


def config_notify_gwm(data=None):
    global GWM_HOST
    if data:
        for node in data.children:
            if node.key == "Host":
                GWM_HOST = str(node.values[0])
            else:
                warning("Unknown config parameter: %s" % node.key)


def notify_gwm(notification):
    N = notification
    # Encode the data
    data = urlencode(dict(
        host=N.host,
        plugin=N.plugin,
        plugin_instance=N.plugin_instance,
        type=N.type,
        type_instance=N.type_instance,
        time=N.time,
        message=N.message,
        severity=N.severity
    )).encode('utf-8')

    # Log the data
    log_data(data)

    try:
        # Post the data to the GWM_HOST
        urlopen(f"{GWM_HOST}/metrics/alert", data, timeout=10)
    except Exception as e:
        warning(f"Couldn't post notification: {str(e)}")


collectd.register_config(config_notify_gwm)
collectd.register_init(init_notify_gwm)
collectd.register_notification(notify_gwm)
