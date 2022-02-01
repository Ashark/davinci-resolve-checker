# DaVinci Resolve Checker
[![platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)](https://en.wikipedia.org/wiki/Linux)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
![license](https://img.shields.io/github/license/Ashark/davinci-resolve-checker.svg)
![checker version](https://img.shields.io/badge/checker_version-2.5.1-green.svg)

[![davinci-resolve aur version](https://img.shields.io/aur/version/davinci-resolve?label=davinci-resolve)](https://aur.archlinux.org/packages/davinci-resolve)
[![davinci-resolve-studio aur version](https://img.shields.io/aur/version/davinci-resolve-studio?label=davinci-resolve-studio)](https://aur.archlinux.org/packages/davinci-resolve-studio)
[![davinci-resolve-beta aur version](https://img.shields.io/aur/version/davinci-resolve-beta?label=davinci-resolve-beta)](https://aur.archlinux.org/packages/davinci-resolve-beta)
[![davinci-resolve-studio-beta aur version](https://img.shields.io/aur/version/davinci-resolve-studio-beta?label=davinci-resolve-studio-beta)](https://aur.archlinux.org/packages/davinci-resolve-studio-beta)

[![amdgpu-pro-libgl aur version](https://img.shields.io/aur/version/amdgpu-pro-libgl?label=amdgpu-pro-libgl)](https://aur.archlinux.org/packages/amdgpu-pro-libgl)
[![opencl-amd aur version](https://img.shields.io/aur/version/opencl-amd?label=opencl-amd)](https://aur.archlinux.org/packages/opencl-amd)

Check your system configuration and hardware for ability to successfully run DaVinci Resolve.

This project is only targeted for Linux platform. Windows and Hackintosh users should not be interested in this project, as there is no problem for them to install native version for their platform.

It checks GPUs presented in system (shows the driver in use), checks OpenGL drivers (actual renderer string), installed OpenCL drivers.
If script detects configuration problem, it suggests how to solve it.

## Supported distributions:

* Arch Linux
* EndeavourOS
* Garuda Linux
* Manjaro Linux

## Installation:

* Clone this repository.
* Install required dependencies:  
`sudo pacman -S expac mesa-demos python-distro`
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

The script will use the locale set in your machine to display messages in your preferred language. In case it's not implemented, default is `en_US` (United States English).

Override this behavior by providing a `--locale xx_YY` argument to the script call. Example: `--locale pt_BR` for Brazilian Portuguese, or `--locale zh_CN` for Simplified Chinese.

## Contribution:

If you have find some error or want to ask for a feature, open a new issue and describe the problem in detail.

### Localization

Currently, this script displays messages in these locales:

* `en_US` - English, United States
* `pt_BR` - Portiguese, Brazil
* `ru_RU` - Russian, Russian Federation
* `zh_CN` - Chinese, Simplified

To contribute translating the script, add a locale file to the `languages/` directory. Use the `en_US.py` file as a reference.

The name of your file should match exactly the locale identification. For example, if you were to implement translation to French, France, you'd have a `languages/fr_FR.py` file.

After implementing the translation, run `python -m unittest` to certify everything is in order.

If you see any errors, it means your translation dictionary `local_str` has misconfigured keys. Double check against the `en_US.py` file, or open an issue if you need assistance.
