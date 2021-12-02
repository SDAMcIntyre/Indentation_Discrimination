from ctypes import *
import time
import os
import sys
import platform

#############################################################################
# LOAD LIBRARY PATHS
if sys.version_info >= (3,0):
    import urllib.parse

# Dependences
# dlls downloaded from xilab
ximc_dir = 'C:\\LAB DOCUMENTS\\Motor With Aurora\\ximc-2.13.1\\ximc'
# local copy of pyximc
ximc_package_dir = 'C:\\Users\\ilosz01\\Desktop\\AuroraProject\\Motor_Python'
sys.path.append(ximc_package_dir)  # add pyximc.py wrapper to python path

# Depending on your version of Windows, add the path to the required DLLs to the environment variable
# bindy.dll
# libximc.dll
# xiwrapper.dll
if platform.system() == "Windows":
    # Determining the directory with dependencies for windows depending on the bit depth.
    arch_dir = "win64" if "64" in platform.architecture()[0] else "win32" # 
    libdir = os.path.join(ximc_dir, arch_dir)
    if sys.version_info >= (3,8):
        os.add_dll_directory(libdir)
    else:
        os.environ["Path"] = libdir + ";" + os.environ["Path"] # add dll path into an environment variable

try: 
    from pyximc import *
except ImportError as err:
    print ("Can't import pyximc module. The most probable reason is that you changed the relative location of the test_Python.py and pyximc.py files. See developers' documentation for details.")
    exit()
class Motor():

    def __init__(self):
        # max speed accel, decel values are 10000
        self.SPEED = 5000
        self.ACCELERATION = 5000
        self.DECELERATION = 5000
        # ttl pulse duration for aurora (microseconds)
        self.PULSE_DURATION = 65530
        # assert that 1 motor step is 0.0012mm
        self.step_in_mm = 0.0012
        # 1 mm = 1/self.step_in_mm = 833.3333 motor steps
        self.one_mm_in_steps = int(1/self.step_in_mm)
        # known serial numbers for x and y axis
        self.XSERIAL = 12563
        self.YSERIAL = 12580

        # variable 'lib' points to a loaded library
        # note that ximc uses stdcall on win
        sbuf = create_string_buffer(64)
        lib.ximc_version(sbuf)
        print("Library version: " + sbuf.raw.decode().rstrip("\0"))

        # Set bindy (network) keyfile. Must be called before any call to "enumerate_devices" or "open_device" if you
        # wish to use network-attached controllers. Accepts both absolute and relative paths, relative paths are resolved
        # relative to the process working directory. If you do not need network devices then "set_bindy_key" is optional.
        # In Python make sure to pass byte-array object to this function (b"string literal").
        result = lib.set_bindy_key(os.path.join(ximc_dir, "win32", "keyfile.sqlite").encode("utf-8"))
        if result != Result.Ok:
            lib.set_bindy_key("keyfile.sqlite".encode("utf-8")) # Search for the key file in the current directory.

        ####################################################################
        # SEARCH FOR AVAILABLE DEVICES
        # This is device search and enumeration with probing. It gives more information about devices.
        probe_flags = EnumerateFlags.ENUMERATE_PROBE + EnumerateFlags.ENUMERATE_NETWORK
        enum_hints = b"addr="
        # enum_hints = b"addr=" # Use this hint string for broadcast enumerate
        devenum = lib.enumerate_devices(probe_flags, enum_hints)
        # print("Device enum handle: " + repr(devenum))
        # print("Device enum handle type: " + repr(type(devenum)))

        dev_count = lib.get_device_count(devenum)
        print("Device count: " + repr(dev_count))

        controller_name = controller_name_t()
        for dev_ind in range(0, dev_count):
            enum_name = lib.get_device_name(devenum, dev_ind)
            result = lib.get_enumerate_device_controller_name(devenum, dev_ind, byref(controller_name))
            if result == Result.Ok:
                print("Enumerated device #{} name (port name): ".format(dev_ind) + repr(enum_name) + ". Friendly name: " + repr(controller_name.ControllerName) + ".")

        # collect available axes
        self.open_names = []
        # collect respective ids
        self.dev_ids = []

        for i in range(dev_count):
            open_name = lib.get_device_name(devenum, i)
            if type(open_name) is str:
                open_name = open_name.encode()
            self.open_names.append(open_name)

        # if no devices were found exit
        if len(self.open_names) == 0:
            exit(1)

        # get devices ids
        for el in self.open_names:
            # print("\nOpen device " + repr(el))
            device_id = lib.open_device(el)
            self.dev_ids.append(device_id)
            print("Device id: " + repr(device_id))
        # assign correct device ids to axes
        self.my_xaxis_id = None
        self.my_yaxis_id = None
        # get devices serial numbers and assign ids
        for id in self.dev_ids:
            serial = self.get_serial(lib,id)
            if str(self.XSERIAL) == serial:
                self.my_xaxis_id = id
            elif str(self.YSERIAL) == serial:
                self.my_yaxis_id = id

        # end if no match was found
        if self.my_xaxis_id == None or self.my_yaxis_id == None:
            exit(1)

    def get_serial(self,lib, device_id):
        my_serial = None
        x_serial = c_uint()
        result = lib.get_serial_number(device_id, byref(x_serial))
        if result == Result.Ok:
            print("Serial: " + repr(x_serial.value))
            my_serial = repr(x_serial.value)
        return my_serial


    # function to send ttl pulse for aurora on motor stop
    # this requires specific pulse duration
    # inverted signal
    # and enabling sync out on stop in xilab
    def set_ttl_on_stop(self,dev_id):
        sync_settings = sync_out_settings_t()
        lib.get_sync_out_settings(dev_id, byref(sync_settings))
        # set flags for TTL pulse on stop to aurora
        sync_settings.SyncOutFlags = (sync_settings.SyncOutFlags & 0x0F) | SyncOutFlags.SYNCOUT_ENABLED
        sync_settings.SyncOutFlags = (sync_settings.SyncOutFlags & 0x0F) | SyncOutFlags.SYNCOUT_INVERT
        sync_settings.SyncOutFlags = (sync_settings.SyncOutFlags & 0x0F) | SyncOutFlags.SYNCOUT_ONSTOP
        
        sync_settings.SyncOutPulseSteps = self.PULSE_DURATION
        lib.set_sync_out_settings(dev_id, byref(sync_settings))

    # this function sets jerk free flag in power management to unchecked
    # this allows both axes to start almost simultaneously
    def set_jerk_free_flag2uncheck(self,dev_id):
        pow_settings = power_settings_t()
        lib.get_power_settings(dev_id, byref(pow_settings))
        if pow_settings.PowerFlags & PowerFlags.POWER_SMOOTH_CURRENT == PowerFlags.POWER_SMOOTH_CURRENT:
            pow_settings.PowerFlags = pow_settings.PowerFlags & ~PowerFlags.POWER_SMOOTH_CURRENT
        lib.set_power_settings(dev_id, byref(pow_settings))
        
    # calibrate axis speed, acceleration, deceleration
    # set ttl pulse on stop
    def calibrate_axis(self,dev_id):
        # Create move settings structure
        mvst = move_settings_t()
        # Get current move settings from controller x
        lib.get_move_settings(dev_id, byref(mvst))
        time.sleep(0.5)
        # Change current speed, acceleration and deceleration
        mvst.Speed = self.SPEED
        mvst.Accel = self.ACCELERATION
        mvst.Decel = self.DECELERATION
        # Write new move settings to controller x
        lib.set_move_settings(dev_id, byref(mvst))
        time.sleep(0.5)
        # set sending ttl pulse on motor stop
        self.set_ttl_on_stop(dev_id)
        time.sleep(0.5)
        # for the axis to start moving simultaneously
        self.set_jerk_free_flag2uncheck(dev_id)

    # give distance in mm (only int)
    def move(self, device_id, distance):
        # in order to move in mm translate to steps
        current_pos,current_upos = self.get_position(device_id)
        dictance_steps = current_pos + self.one_mm_in_steps * distance
        # print("Going to {0} steps".format(dictance_steps))
        lib.command_move(device_id, dictance_steps, current_upos)

    def get_position(self, device_id):
        x_pos = get_position_t()
        result = lib.get_position(device_id, byref(x_pos))
        # if result == Result.Ok:
        #     print("Position: {0} steps, {1} microsteps".format(x_pos.Position, x_pos.uPosition))
        return x_pos.Position, x_pos.uPosition