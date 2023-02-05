# goto

a terminal project switcher

![goto](./res/goto_demo.gif)

## Installation

```bash
# clone the repository
git clone https://github.com/zhooda/goto

# install Python dependencies
# NOTE: only needed for building,
#       you can uninstall after
python3 -m pip install black isort

# build the script
make build

# install to /usr/local/bin
sudo make install
# or install to a custom location
make install INSTALL_DIR=/path/to/bin

# clean build files
make clean
# uninstall
sudo make distclean

# uninstall Python dependencies (if needed)
python3 -m pip uninstall black isort
```

## Usage

```
goto: a terminal project switcher

usage:
    goto [PROJECT_NAME]                    - switch to named project
    goto -r [PROJECT_NAME] [PROJECT_PATH]  - register new project path  [-r/--register]
    goto -d [PROJECT_NAME]                 - remove project from config [-d/--delete]
    goto -l                                - list all project configs   [-l/--list]
    goto -h                                - print this help message    [-h/--help]
```
