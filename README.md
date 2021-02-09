# DaVinci Resolve Checker
[![Generic badge](https://img.shields.io/badge/platform-linux-lightgrey.svg)](https://en.wikipedia.org/wiki/Linux)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)


[![davinci-resolve aur version](https://img.shields.io/aur/version/davinci-resolve?label=davinci-resolve)](https://aur.archlinux.org/packages/davinci-resolve)
[![davinci-resolve-studio aur version](https://img.shields.io/aur/version/davinci-resolve?label=davinci-resolve-studio)](https://aur.archlinux.org/packages/davinci-resolve)
[![davinci-resolve-beta aur version](https://img.shields.io/aur/version/davinci-resolve?label=davinci-resolve-beta)](https://aur.archlinux.org/packages/davinci-resolve-beta)
[![davinci-resolve-studio-beta aur version](https://img.shields.io/aur/version/davinci-resolve?label=davinci-resolve-studio-beta)](https://aur.archlinux.org/packages/davinci-resolve-studio-beta)

Check your system configuration and hardware for ability to successfully run DaVinci Resolve.

This project is only targeted for Linux platform. Windows and Hackintosh users should not be interested in this project, as there is no problem for them to install native version for their platform.

It checks GPUs presented in system (shows the driver in use), checks OpenGL drivers (actual renderer string), installed OpenCL drivers.
If script detects configuration problem, it suggests how to solve it.

## Supported distributions:

* Arch Linux
* Manjaro Linux
* EndeavourOS

## Installation:

* Clone this repository.
* Install required dependencies:  
`sudo pacman -S python-distro expac glxinfo`
* Install other required dependencies from aur (assuming you use yay):  
`yay -S python-pylspci`

## Usage:

Run the script with the same parameters as you intend to launch D.R.
For example, if using Nvidia Optimus laptop, you probably use prime-run, so run:
`prime-run ./davinci-resolve-checker.py`

The output of the script should be the following:
```
DaVinci Resolve checker 1.4.1
...
All seems good. You should be able to run DaVinci Resolve successfully.
```

If you have some problem, the script will tell you what is wrong with your configuration, for example:
```
DaVinci Resolve checker 1.4.1
Chassis type: desktop
Installed OpenCL drivers: opencl-amd-polaris opencl-nvidia
Presented GPUs:
        UHD Graphics 630 (Desktop) (kernel driver in use: i915)
        Ellesmere [Radeon RX 470/480/570/570X/580/580X/590] (kernel driver in use: amdgpu)
OpenGL vendor string: Intel

Your primary gpu is Intel. Go to your uefi settings and set primary display to PCIE. Otherwise you could not use DaVinci Resolve (I did not tested it).
```

## Contribution:
If you have find some error or want to ask for a feature, open a new issue and describe the problem in detail.
