# DaVinci Resolve Checker

Check your system configuration and hardware for ability to successfully run DaVinci Resolve.

This project is only targeted for Linux platform. Windows and Hackintosh users should not be interested in this project, as there is no problem for them to install native version for their platform.

It checks GPUs presented in system, checks OpenGL drivers (actual renderer string), OpenCL drivers.


## Supported distributions:

* Arch Linux
* Manjaro Linux
* EndeavourOS

## Installation:

* Clone this repository.
* Install required dependencies:  
`sudo pacman -S python-distro expac glxinfo`
* Install `pylspci` with pip (because in Arch Linux there is no `python-pylspci` in AUR yet):  
`sudo pacman -S python-pip && pip install pylspci` 

## Usage:

Run the script with the same parameters as you intend to launch D.R.
For example, if using Nvidia Optimus laptop, you probably use prime-run, so run:
`prime-run ./davinci-resolve-checker.py`

The output of the script should be the following:
```
DaVinci Resolve checker 1.3.2
...
All seems good. You should be able to run DaVinci Resolve successfully.
```

If you have some problem, the script will tell you what is wrong with your configuration, for example:
```
DaVinci Resolve checker 1.3.2
Your configuration:
Chassis: desktop
Installed OpenCL drivers: opencl-amdgpu-pro-orca opencl-nvidia
Presented GPUs:
        UHD Graphics 630 (Desktop) driver: i915
        Ellesmere [Radeon RX 470/480/570/570X/580/580X/590] driver: vfio-pci
OpenGL vendor string: Intel
You are not using amdgpu as kernel driver. Set radeon.si/cik_support=0 and amdgpu.si/cik_support=1 kernel parameters, otherwise you could not use DaVinci Resolve.
```

## Contribution:
If you have find some error or want to ask for a feature, open a new issue and describe the problem in detail.
