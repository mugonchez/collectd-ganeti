# coding: utf-8
import collectd
from discover_vm import discover


def config_cpu_wait(data=None):
    collectd.debug("Configuration: " + repr(data))


def init_cpu_wait(data=None):
    collectd.debug("Initialization: " + repr(data))
