#!/bin/python
import distro
import subprocess
import re
import pylspci

print("DaVinci Resolve checker", "1.2.1")

if distro.id() not in {"arch", "manjaro"}:
    print("You are running", distro.name(), "but this script was not tested on it.")
    exit(1)

machine_info = subprocess.check_output(["hostnamectl", "status"], universal_newlines=True)
m = re.search('Chassis: (.+?)\n', machine_info)
chassis_type = m.group(1)

installed_opencl_drivers = subprocess.getoutput("expac -Qs '%n' opencl-driver").splitlines()

from pylspci.parsers import VerboseParser
lspci_devices = VerboseParser().run()

# Now we are going to check which GPUs are presented in system.
# According to this link: https://pci-ids.ucw.cz/read/PD/03
# There are four subclasses in PCI 03xx class
# I have seen all of them in machines that I could test, except 0301 - XGA controller
# lspci -d ::0300 - intel gpu or amd primary gpu
# lspci -d ::0302 - nvidia 3d controller on an optimus laptop
# lspci -d ::0380 - amd secondary gpu on an i+a laptop

found_AMD_GPU = None
found_INTEL_GPU = None
found_NVIDIA_GPU = None

for device in lspci_devices:
    if device.cls.id in (0x0300, 0x0301, 0x0302, 0x0380):
        if device.vendor.name == 'Intel Corporation':
            if found_INTEL_GPU == None:
                found_INTEL_GPU = device
            else:
                print("You have several INTEL GPUs. I am confused. Are you using multi-cpu desktop motherboard?")
                exit(1)
        if device.vendor.name == 'Advanced Micro Devices, Inc. [AMD/ATI]':
            if found_AMD_GPU == None:
                found_AMD_GPU = device
            else:
                print("You have several AMD GPUs. I am confused. Which one do you intend to use?")
                exit(1)
        if device.vendor.name == 'NVIDIA Corporation':
            if found_NVIDIA_GPU == None:
                found_NVIDIA_GPU = device
            else:
                print("You have several NVIDIA GPUs. I am confused. Which one do you intend to use?")
                exit(1)

if found_AMD_GPU and found_NVIDIA_GPU:
    print("You have AMD and NVIDIA GPUs. I am confused. Which one do you intend to use?")
    exit(1)
if not found_AMD_GPU and not found_NVIDIA_GPU and found_INTEL_GPU:
        print("You have only Intel GPU. Currently DR cannot use intel GPUs for OpenCL. You cannot run DR. See https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=81579")
        exit(1)

if found_AMD_GPU:
    if chassis_type == 'desktop':
        if found_AMD_GPU.driver != 'amdgpu':
            print("You are not using amdgpu as kernel driver. Set radeon.si/cik_support=0 and amdgpu.si/cik_support=1 kernel parameters, otherwise you could not use DaVinci Resolve.")
            exit(1)
        if subprocess.getoutput('glxinfo | grep "OpenGL vendor string" | cut -f2 -d":" | xargs') != "Advanced Micro Devices, Inc.":
            print("You are not running AMDGPU-PRO renderer. Install amdgpu-pro-libgl, otherwise you could not use DaVinci Resolve.")
            exit(1)
        if 'opencl-amdgpu-pro-orca' in installed_opencl_drivers or 'opencl-amdgpu-pro-pal' in installed_opencl_drivers:
            print("All seems good. You should be able to run DaVinci Resolve successfully.")
    elif chassis_type == 'laptop':
        print("I did not found a working configuration with AMD gpu on laptop yet. Did you?")

if found_NVIDIA_GPU:
    # I have tested it with D.R. 16.2.3 and found out that BMD have fixed that issue. See https://www.youtube.com/watch?v=NdOGFBHEnkU
    # So I will keep this comment for a while, then will remove it.
    # if 'opencl-amdgpu-pro-orca' in installed_opencl_drivers or 'opencl-amdgpu-pro-pal' in installed_opencl_drivers or 'opencl-amd' in installed_opencl_drivers:
    #     print("You have installed opencl for amd, but DaVinci Resolve stupidly crashes if it is presented with nvidia gpu. Remove it, otherwise you could not use DaVinci Resolve.")
    if 'opencl-nvidia' not in installed_opencl_drivers:
        print("You do not have opencl-nvidia package. Install it, otherwise you could not use D.R. Even if you are planning to use cuda, opencl-nvidia will be installed as its dependency.")
        exit(1)
    if found_NVIDIA_GPU.driver != 'nvidia':
        print("You are not using nvidia as kernel driver. Use proprietary nvidia driver, otherwise you could not use DaVinci Resolve.")
        exit(1)
    if subprocess.getoutput('glxinfo | grep "OpenGL vendor string" | cut -f2 -d":" | xargs') != "NVIDIA Corporation":
        print("You are not running NVIDIA renderer. Try to run the script with prime-run or other method for optimus, otherwise you could not use DaVinci Resolve.")
        exit(1)
    print("All seems good. You should be able to run DaVinci Resolve successfully.")
