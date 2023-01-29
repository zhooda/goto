# goto

a terminal project switcher

## Installation

```bash
# clone the repository
git clone https://github.com/zhooda/goto

# symlink to /usr/local/bin or wherever
# you keep user installed binaries
ln -s goto/goto.py /usr/local/bin/goto
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
