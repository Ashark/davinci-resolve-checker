#!/usr/bin/env python3

import distro
import subprocess
import re
import pylspci

print("达芬奇调色检测工具", "1.6.2") # When bumping, do not forget to also bump it in readme.

if distro.id() not in {"arch", "manjaro", "endeavouros"}:
    print("您使用的是", distro.name(), "(", distro.id(), ") 发行版本，但是本脚本尚未在该发行版上进行测试")
    exit(1)

installed_dr_package = subprocess.run("expac -Qs '%n %v' davinci-resolve", shell=True, capture_output=True, text=True).stdout.rstrip('\n')
print("已安装达芬奇调试: " + installed_dr_package)

machine_info = subprocess.check_output(["hostnamectl", "status"], text=True)
m = re.search('Chassis: (.+?)\n', machine_info)
chassis_type = m.group(1)

installed_opencl_drivers = subprocess.check_output("expac -Qs '%n' opencl-driver", shell=True, text=True).splitlines()
installed_opencl_nvidia_package = subprocess.run("expac -Qs '%n' opencl-nvidia", shell=True, capture_output=True, text=True).stdout.rstrip('\n')

from pylspci.parsers import VerboseParser
lspci_devices = VerboseParser().run()

print("设备类型: " + chassis_type)
print("已安装的OpenCL驱动: " + " ".join([str(x) for x in installed_opencl_drivers]))

# Now we are going to check which GPUs are presented in system.
# According to this link: https://pci-ids.ucw.cz/read/PD/03
# There are four subclasses in PCI 03xx class
# I have seen all of them in machines that I could test, except 0301 - XGA controller
# lspci -d ::0300 - intel gpu or amd primary gpu
# lspci -d ::0302 - nvidia 3d controller on an optimus laptop
# lspci -d ::0380 - amd secondary gpu on an i+a laptop

print("显卡型号:")
print ("\t" + "\n\t".join([ x.device.name + " (内核驱动: " + x.driver + ")" for x in lspci_devices if x.cls.id in (0x0300, 0x0301, 0x0302, 0x0380) ]))

GL_VENDOR = subprocess.check_output('glxinfo | grep "OpenGL vendor string" | cut -f2 -d":"', shell=True, text=True).strip()
print("OpenGL供应商: " + GL_VENDOR)
# By GL_VENDOR we can distinguish not only OpenGL Open/Pro implementations, but also a primary GPU in use (kinda).
# See https://stackoverflow.com/questions/19985131/how-identify-the-primary-video-card-on-linux-programmatically for more information.

print("")  # Empty line, to separate verdict from configuration info.

if GL_VENDOR == "":
    print("无法查询OpenGL供应商信息。您的显卡型号可能是Intel，然而您在尝试使用AMD Pro OpenGL或您在SSH环境下运行本程序。")
    exit(1)

if "opencl-mesa" in installed_opencl_drivers:
    print("您需要卸载opencl-mesa，否则达芬奇(v17.1.1)将无法运行: 镜像已损坏。但是如果您在设置中反选gpu复选框然后重新启动达芬奇，那么可能会导致整个桌面会话都会损坏，您只能重新启动您的电脑。 至少在AMD显卡上可以观察到这一点。")
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
                print("检测到您有多个INTEL显卡。您是否在使用多CPU台式机主板？还是intel igpu + intel dgpu（在编写本程序的时候尚未发现这一现象）？")
                exit(1)
        if device.vendor.name == 'Advanced Micro Devices, Inc. [AMD/ATI]':
            if found_AMD_GPU == None:
                found_AMD_GPU = device
            else:
                print("检测到您有多个AMD显卡。您准备使用哪一个？")
                exit(1)
        if device.vendor.name == 'NVIDIA Corporation':
            if found_NVIDIA_GPU == None:
                found_NVIDIA_GPU = device
            else:
                print("检测到您有多个NVIDIA显卡。您准备使用哪一个？")
                exit(1)

if found_AMD_GPU and found_NVIDIA_GPU:
    if found_AMD_GPU.driver != "vfio-pci" and found_NVIDIA_GPU.driver != "vfio-pci":
        print("检测到您有AMD和NVIDIA显卡。您准备使用哪一个？")
        exit(1)
    else:
        if found_AMD_GPU.driver == "vfio-pci":
            print("您的AMD显卡已绑定到 vfio-pci，将不再进行进一步检查。")
            found_AMD_GPU = None
        if found_NVIDIA_GPU.driver == "vfio-pci":
            print("您的NVIDIA显卡已绑定到 vfio-pci，将不再进行进一步检查。")
            found_NVIDIA_GPU = None

if not found_AMD_GPU and not found_NVIDIA_GPU and found_INTEL_GPU:
        print("您只有英特尔显卡。目前达芬奇无法将英特尔显卡用于OpenCL。因此您不能运行达芬奇。详情请参考https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=81579")
        exit(1)

if found_AMD_GPU:
    if found_INTEL_GPU:
        if chassis_type == 'laptop':
            print("暂未找到适用于英特尔+AMD显卡的笔记本电脑的工作配置。您是不是使用的这个型号的笔记本？")
            exit(1)
        elif GL_VENDOR == "Intel":
            print("检测到您的主显卡是英特尔。您可以在UEFI设置中将主显示器设置为PCIE。否则您将无法使用DaVinci Resolve（尚未测试）。")
            exit(1)

    if found_AMD_GPU.driver != 'amdgpu':
        if found_AMD_GPU.driver == 'radeon':
            if 'amdgpu' in found_AMD_GPU.kernel_modules and 'radeon' in found_AMD_GPU.kernel_modules:
                print('您当前正在使用RADEON驱动程序。请参照ArchWiki将驱动程序切换到amdgpu：https://wiki.archlinux.org/title/AMDGPU#Enable_Southern_Islands_(SI)_and_Sea_Islands_(CIK)_support。否则您将无法运行达芬奇。')
                exit(1)
            else:
                print("您的GPU仅支持radeon驱动程序。达芬奇需要使用amdgpu progl才能运行，因为它只能与amdgpu驱动一起使用。因此，您无法运行达芬奇。")
        print("出于某种原因，您没有运行amdgpu驱动程序。 您无法运行达芬奇。")
        exit(1)

    if GL_VENDOR != "Advanced Micro Devices, Inc.":
        # Note: If you run "progl glmark2", you see there "GL_VENDOR:     ATI Technologies Inc.",
        # but if you run "progl glxinfo", you always get "OpenGL vendor string: Advanced Micro Devices, Inc."
        # independently of you use X or Wayland; I+A, A+I or just AMD gpu in system.
        # So we check if it is "Advanced Micro Devices, Inc.".
        print("您没有使用Pro OpenGL。请安装amdgpu-pro-libgl并在运行达芬奇的时候使用progl前缀运行。否则程序可能会闪退或无法运行。")
        exit(1)

    if 'opencl-amd' not in installed_opencl_drivers and 'opencl-amd-polaris' not in installed_opencl_drivers:
        print("您的计算机没有用于AMD显卡的opencl驱动程序。请安装该驱动程序，否则您无法使用达芬奇。")
        exit(1)
    else:
        print("恭喜您，您可以正常使用达芬奇了！")
        # exit(0)

if found_NVIDIA_GPU:
    # I have tested it with DR 16.2.3 and found out that BMD have fixed that issue. See https://www.youtube.com/watch?v=NdOGFBHEnkU
    # So I will keep this comment for a while, then will remove it.
    # if 'opencl-amdgpu-pro-orca' in installed_opencl_drivers or 'opencl-amdgpu-pro-pal' in installed_opencl_drivers or 'opencl-amd' in installed_opencl_drivers:
    #     print("You have installed opencl for amd, but DaVinci Resolve stupidly crashes if it is presented with nvidia gpu. Remove it, otherwise you could not use DaVinci Resolve.")
    if not installed_opencl_nvidia_package:
        print("您没有opencl-nvidia包（或提供opencl-nvidia的替代包）。请务必安装它，否则您将无法使用达芬奇。即使您打算使用cuda，opencl-nvidia也是其必需的依赖项。")
        exit(1)
    if found_NVIDIA_GPU.driver != 'nvidia':
        print("您没有使用nvidia作为内核驱动程序。请使用专有的nvidia驱动程序，否则您将无法使用达芬奇。")
        exit(1)
    if GL_VENDOR != "NVIDIA Corporation":
        print("您没有运行NVIDIA渲染器。尝试使用prime-run或其他optimus方法运行脚本，否则无法确保您可以正常使用使用达芬奇。")
        exit(1)
    print("恭喜您，您可以正常使用达芬奇了！")
