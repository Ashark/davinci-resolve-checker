#!/usr/bin/env python3

import distro
import subprocess
import re
import pylspci

print("DaVinci Resolve checker", "1.6.2") # When bumping, do not forget to also bump it in readme.

if distro.id() not in {"arch", "manjaro", "endeavouros"}:
    print("You are running", distro.name(), "(", distro.id(), ") but this script was not tested on it.")
    exit(1)

installed_dr_package = subprocess.run("expac -Qs '%n %v' davinci-resolve", shell=True, capture_output=True, text=True).stdout.rstrip('\n')
print("Installed DaVinci Resolve package: " + installed_dr_package)

machine_info = subprocess.check_output(["hostnamectl", "status"], text=True)
m = re.search('Chassis: (.+?)\n', machine_info)
chassis_type = m.group(1)

installed_opencl_drivers = subprocess.check_output("expac -Qs '%n' opencl-driver", shell=True, text=True).splitlines()
installed_opencl_nvidia_package = subprocess.run("expac -Qs '%n' opencl-nvidia", shell=True, capture_output=True, text=True).stdout.rstrip('\n')

from pylspci.parsers import VerboseParser
lspci_devices = VerboseParser().run()

print("Chassis type: " + chassis_type)
print("Installed OpenCL drivers: " + " ".join([str(x) for x in installed_opencl_drivers]))

# Now we are going to check which GPUs are presented in system.
# According to this link: https://pci-ids.ucw.cz/read/PD/03
# There are four subclasses in PCI 03xx class
# I have seen all of them in machines that I could test, except 0301 - XGA controller
# lspci -d ::0300 - intel gpu or amd primary gpu
# lspci -d ::0302 - nvidia 3d controller on an optimus laptop
# lspci -d ::0380 - amd secondary gpu on an i+a laptop

print("Presented GPUs:")
print ("\t" + "\n\t".join([ x.device.name + " (kernel driver in use: " + x.driver + ")" for x in lspci_devices if x.cls.id in (0x0300, 0x0301, 0x0302, 0x0380) ]))

GL_VENDOR = subprocess.check_output('glxinfo | grep "OpenGL vendor string" | cut -f2 -d":"', shell=True, text=True).strip()
print("OpenGL vendor string: " + GL_VENDOR)
# By GL_VENDOR we can distinguish not only OpenGL Open/Pro implementations, but also a primary GPU in use (kinda).
# See https://stackoverflow.com/questions/19985131/how-identify-the-primary-video-card-on-linux-programmatically for more information.

print("")  # Empty line, to separate verdict from configuration info.

if GL_VENDOR == "":
    print("Unable to detect the OpenGL vendor string. Probably you are trying to use AMD Pro OpenGL while your primary GPU is Intel. Also probably you are launching script via ssh.")
    exit(1)

if "opencl-mesa" in installed_opencl_drivers:
    print("You should uninstall opencl-mesa. Otherwise DR (v17.1.1) behaves wrong: image is corrupted. But if you uncheck gpu checkbox in settings and relaunch DR, then even entire desktop session becomes corrupted and you only can reboot your pc. This is observed at least on amd gpu.")
    exit(1)

found_AMD_GPU = None
found_INTEL_GPU = None
found_NVIDIA_GPU = None

for device in lspci_devices:
    if device.cls.id in (0x0300, 0x0301, 0x0302, 0x0380):
        if device.vendor.name == 'Intel Corporation':
            if found_INTEL_GPU == None:
                found_INTEL_GPU = device
            else:
                print("You have several INTEL GPUs. I am confused. Are you using multi-cpu desktop motherboard? Or intel igpu + intel dgpu (which does not exist at the moment of writing)?")
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
    if found_AMD_GPU.driver != "vfio-pci" and found_NVIDIA_GPU.driver != "vfio-pci":
        print("You have AMD and NVIDIA GPUs. I am confused. Which one do you intend to use?")
        exit(1)
    else:
        if found_AMD_GPU.driver == "vfio-pci":
            print("Your amd gpu is binded to vfio-pci, dropping it from further checking.")
            found_AMD_GPU = None
        if found_NVIDIA_GPU.driver == "vfio-pci":
            print("Your nvidia gpu is binded to vfio-pci, dropping it from further checking.")
            found_NVIDIA_GPU = None

if not found_AMD_GPU and not found_NVIDIA_GPU and found_INTEL_GPU:
        print("You have only Intel GPU. Currently DR cannot use intel GPUs for OpenCL. You cannot run DR. See https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=81579")
        exit(1)

if found_AMD_GPU:
    if found_INTEL_GPU:
        if chassis_type == 'laptop':
            print("I did not found a working configuration yet for laptops with Intel + AMD graphics. Did you?")
            exit(1)
        elif GL_VENDOR == "Intel":
            print("Your primary gpu is Intel. Go to your uefi settings and set primary display to PCIE. Otherwise you could not use DaVinci Resolve (I did not tested it).")
            exit(1)

    if found_AMD_GPU.driver != 'amdgpu':
        if found_AMD_GPU.driver == 'radeon':
            if 'amdgpu' in found_AMD_GPU.kernel_modules and 'radeon' in found_AMD_GPU.kernel_modules:
                print("You are currently using radeon driver. Switch to amdgpu as described here: https://wiki.archlinux.org/title/AMDGPU#Enable_Southern_Islands_(SI)_and_Sea_Islands_(CIK)_support. Otherwise you could not run DaVinci Resolve.")
                exit(1)
            else:
                print("Your gpu only supports radeon driver. DaVinci Resolve requires amdgpu progl, which can only work with amdgpu driver. You cannot run DaVinci Resolve.")
        print("For some reason, you are not running amdgpu driver. You cannot run DaVinci Resolve.")
        exit(1)

    if GL_VENDOR != "Advanced Micro Devices, Inc.":
        # Note: If you run "progl glmark2", you see there "GL_VENDOR:     ATI Technologies Inc.",
        # but if you run "progl glxinfo", you always get "OpenGL vendor string: Advanced Micro Devices, Inc."
        # independently of you use X or Wayland; I+A, A+I or just AMD gpu in system.
        # So we check if it is "Advanced Micro Devices, Inc.".
        print("You are not using Pro OpenGL implementation. Install amdgpu-pro-libgl and run DaVinci Resolve with progl prefix. Otherwise it will crash.")
        exit(1)

    if 'opencl-amd' not in installed_opencl_drivers and 'opencl-amd-polaris' not in installed_opencl_drivers:
        print("You do not have opencl-driver for AMD GPU. Install it, otherwise you could not use DaVinci Resolve.")
        exit(1)
    else:
        print("All seems good. You should be able to run DaVinci Resolve successfully.")
        # exit(0)

if found_NVIDIA_GPU:
    # I have tested it with DR 16.2.3 and found out that BMD have fixed that issue. See https://www.youtube.com/watch?v=NdOGFBHEnkU
    # So I will keep this comment for a while, then will remove it.
    # if 'opencl-amdgpu-pro-orca' in installed_opencl_drivers or 'opencl-amdgpu-pro-pal' in installed_opencl_drivers or 'opencl-amd' in installed_opencl_drivers:
    #     print("You have installed opencl for amd, but DaVinci Resolve stupidly crashes if it is presented with nvidia gpu. Remove it, otherwise you could not use DaVinci Resolve.")
    if not installed_opencl_nvidia_package:
        print("You do not have opencl-nvidia package (or alternative package which provides opencl-nvidia). Install it, otherwise you could not use DR. Even if you are planning to use cuda, opencl-nvidia is its required dependency.")
        exit(1)
    if found_NVIDIA_GPU.driver != 'nvidia':
        print("You are not using nvidia as kernel driver. Use proprietary nvidia driver, otherwise you could not use DaVinci Resolve.")
        exit(1)
    if GL_VENDOR != "NVIDIA Corporation":
        print("You are not running NVIDIA renderer. Try to run the script with prime-run or other method for optimus, otherwise you could not use DaVinci Resolve.")
        exit(1)
    print("All seems good. You should be able to run DaVinci Resolve successfully.")
