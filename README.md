# DaVinci Resolve Checker

Check your system configuration and hardware for ability to successfully run DaVinci Resolve.

This project is only targeted for Linux platform. Windows and Hackintosh users should not be interested in this project, as there is no problem for them to install native version for their platform.

It checks GPUs presented in system, checks OpenGL drivers (actual renderer string), OpenCL drivers.


## Supported distributions:

* Arch Linux
* Manjaro Linux

## Installation:

* Clone this repository.
* Install `pylspci` with pip (because in Arch Linux there is no `python-pylspci` in AUR yet): `pip install pylspci` 
* Install `distro` with pip.
* Install the `expac` and `glxinfo` packages.

## Usage:

Run the script with the same parameters as you intend to launch D.R.
For example, if using Nvidia Optimus laptop, you probably use prime-run, so run:
`prime-run ./davinci-resolve-checker.py`

The output of the script should be the following:
```
DaVinci Resolve checker 1.0.0
All seems good. You should be able to run DaVinci Resolve successfully.
```

If you have some problem, the script will tell you what is wrong with your configuration, for example:
```
DaVinci Resolve checker 1.0.0
You are not running AMDGPU-PRO renderer. Install amdgpu-pro-libgl, otherwise you could not use DaVinci Resolve.
```

## Contribution:
If you have find some error or want to ask for a feature, open a new issue and describe the problem in detail.
