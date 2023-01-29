#!/usr/bin/env python3

import argparse
import json
import os
import signal

from term_col import TermCol


class GotoConfig:
    def __init__(self, path=None):
        self.path = (
            path
            if path is not None
            else os.path.join(
                os.path.expanduser("~"), ".config", "goto", "projects.json"
            )
        )

        _, err = self.load()
        if err is not None:
            raise EnvironmentError(err)

    @property
    def projects(self):
        return self.data["projects"]

    def add_project(self, name, path):
        """
        Add a project to the config file.

        Args:
            name (str): The name of the project to add.
            path (str): The path to the project to add.

        Returns:
            (bool, str): A tuple containing a boolean indicating whether the
                project was added or not and a string containing an error
                message if there were errors.
        """

        full_path = os.path.normcase(os.path.abspath(os.path.expanduser(path)))
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            return (
                None,
                f"'{TermCol.MG(full_path)}' does not exist or is not a directory",
            )
        if name in self.data["projects"]:
            return None, f"project '{TermCol.MG(name)}' already exists"
        self.projects[name] = full_path

        _, err = self.save()
        if err is not None:
            return None, err

        return True, None

    def get_project(self, name):
        """
        Get a project from the config file.

        Args:
            name (str): The name of the project to get.

        Returns:
            (str, str): A tuple containing the path to the project or a string
                containing an error message if there were errors.
        """

        if name in self.projects:
            return self.projects[name], None
        return None, f"project '{TermCol.MG(name)}' does not exist"

    def remove_project(self, name):
        """
        Remove a project from the config file.

        Args:
            name (str): The name of the project to remove.

        Returns:
            (bool, str): A tuple containing a boolean indicating whether the
                project was removed or a string containing an error message
                if there were errors.
        """

        if name not in self.data["projects"]:
            return False, f"project '{TermCol.MG(name)}' does not exist"
        del self.projects[name]

        _, err = self.save()
        if err is not None:
            return False, err
        return True, None

    def list_projects(self):
        """
        Print all projects in the config file to stdout
        """

        if len(self.projects) == 0:
            print(TermCol.WH_B("projects:"))
            return

        formatted_config = {
            TermCol.MG_B(key) + "@": TermCol.BL_UL(value)
            for key, value in self.projects.items()
        }
        formatted_config = dict(sorted(formatted_config.items()))
        max_key_length = max(len(key) for key in formatted_config.keys())

        print(TermCol.WH_B("projects:"))
        for key, value in formatted_config.items():
            print(f"    {key:<{max_key_length+2}} {TermCol.ARROW}  {value}")

    def load(self):
        """
        Load the config file.

        Returns:
            (bool, str): A tuple containing a boolean indicating whether the
                config was loaded or a string containing an error message
                if there were errors.
        """

        if not os.path.exists(self.path):
            self.data = {"projects": {}}

            _, err = self.save()
            if err is not None:
                return False, err
        try:
            with open(self.path, "r") as f:
                self.data = json.load(f)
            return True, None
        except Exception as e:
            return False, f"{e}"

    def save(self):
        """
        Save the config file.

        Returns:
            (bool, str): A tuple containing a boolean indicating whether the
                config was saved or a string containing an error message
                if there were errors.
        """

        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            with open(self.path, "w") as f:
                json.dump(self.data, f)
            return True, None
        except Exception as e:
            return False, f"{e}"


def spawn_shell_and_kill(new_path):
    pid = os.getppid()
    os.chdir(new_path)
    os.system("$SHELL")
    os.kill(pid, signal.SIGKILL)


def handle_error(err, usage=None, exit_code=1, should_exit=True):
    print(TermCol.RD_NB("error:"), end=" ")
    if usage is not None:
        print(usage.strip(), end="\n    ")
    print(err)
    if should_exit:
        exit(exit_code)


def resolve_flag(flag):
    if flag in ["-r", "--register"]:
        return "register"
    if flag in ["-d", "--delete"]:
        return "delete"
    if flag in ["-l", "--list"]:
        return "list"
    if flag in ["-h", "--help"]:
        return "help"
    return None


def usage(name="goto", flag=None):
    binary = TermCol.BL(name)
    name_arg = "[PROJECT_NAME]"
    path_arg = "[PROJECT_PATH]"
    flags = {
        "-r": TermCol.GR_B("-r"),
        "-d": TermCol.RD_B("-d"),
        "-l": TermCol.BL_B("-l"),
        "-h": TermCol.YL_B("-h"),
    }
    messages = {
        "about": TermCol.MG_B("goto") + ": a terminal project switcher\n",
        "main": TermCol.NC_B("usage:"),
        "switch": f"    {binary} {TermCol.MG_B(name_arg)}                    - switch to named project",
        "register": f"    {binary} {flags['-r']} {TermCol.GR_B(name_arg)} {TermCol.GR_B(path_arg)}  - register new project path  [-r/--register]",
        "delete": f"    {binary} {flags['-d']} {TermCol.RD_B(name_arg)}                 - remove project from config [-d/--delete]",
        "list": f"    {binary} {flags['-l']}                                - list all project configs   [-l/--list]",
        "help": f"    {binary} {flags['-h']}                                - print this help message    [-h/--help]",
    }

    if flag is None:
        return "\n".join(messages.values())

    return messages.get(resolve_flag(flag), "").strip().split(" - ")[0]


def parse_args(args=None):
    import sys

    _args = args[1:].copy() if args is not None else sys.argv[1:]
    parsed_args = {"invalid": [], "error": "", "ret_code": 0, "action": None}

    def check_len(flag, iterable, expected_len):
        """Check if the length of an iterable is equal to the expected length.
        Returns True if correct, False if not."""
        if len(iterable) != expected_len:
            parsed_args[
                "error"
            ] = f"expected {expected_len} argument(s), received {len(iterable)}"
            parsed_args["action"] = flag
            parsed_args["ret_code"] = 1
            return False
        return True

    if len(_args) == 0:
        parsed_args["error"] = "expected at least one argument, received 0"
        parsed_args["ret_code"] = 1
        return argparse.Namespace(**parsed_args)

    arg = _args.pop(0)
    if arg in ("-r", "--register"):
        if check_len(arg, _args, 2):
            parsed_args["action"] = "register"
            parsed_args["project_name"] = _args.pop(0)
            parsed_args["project_path"] = _args.pop(0)
    elif arg in ("-d", "--delete"):
        if check_len(arg, _args, 1):
            parsed_args["action"] = "delete"
            parsed_args["project_name"] = _args.pop(0)
    elif arg in ("-l", "--list"):
        if check_len(arg, _args, 0):
            parsed_args["action"] = "list"
    elif arg in ("-h", "--help"):
        if check_len(arg, _args, 0):
            parsed_args["action"] = "help"
    elif len(_args) == 0:
        parsed_args["action"] = "switch"
        parsed_args["project_name"] = arg
    else:
        parsed_args["invalid"].append(arg)
        parsed_args["error"] = "invalid argument(s)"
        parsed_args["ret_code"] = 1

    return argparse.Namespace(**parsed_args)


if __name__ == "__main__":
    args = parse_args()

    if args.action == "help" or args.action is None:
        print(usage())
        exit(args.ret_code)
    if args.ret_code != 0:
        if args.error:
            handle_error(
                args.error, usage=usage(flag=args.action), exit_code=args.ret_code
            )

    try:
        config = GotoConfig()
    except EnvironmentError as e:
        handle_error(e)

    if args.action == "register":
        did_add, err = config.add_project(args.project_name, args.project_path)
        if err != None:
            handle_error(err)
    elif args.action == "delete":
        did_remove, err = config.remove_project(args.project_name)
        if err != None:
            handle_error(err)
    elif args.action == "list":
        config.list_projects()
    elif args.action == "switch":
        path, err = config.get_project(args.project_name)
        if err != None:
            handle_error(err)
        spawn_shell_and_kill(path)

# if __name__ == "__main__":

#     config = load_config()

#     if len(sys.argv) == 1:
#         binary = TermCol.WH_F(
#             sys.argv[0]
#             if os.environ.get("GOTO_USE_FULL_PATH", False) == "1"
#             else "goto"
#         )
#         name_arg = TermCol.GR_B("[PROJECT_NAME]")
#         path_arg = TermCol.GR_B("[PROJECT_PATH]")
#         flags = {
#             "-r": TermCol.RD_B("-r"),
#             "-d": TermCol.RD_B("-d"),
#             "-l": TermCol.RD_B("-l"),
#         }
#         print(
#             "\n".join(
#                 [
#                     TermCol.NC_B("Usage:"),
#                     f"    {binary} {name_arg}                    - switch to named project",
#                     f"    {binary} {flags['-r']} {name_arg} {path_arg}  - register new project path",
#                     f"    {binary} {flags['-d']} {name_arg}                 - remove project from config",
#                     f"    {binary} {flags['-l']}                                - list all project configs",
#                 ]
#             )
#         )
#         exit(0)

#     reserved = ["-r", "-d", "-l"]

#     if len(sys.argv) == 2 and sys.argv[1] == "-l":
#         formatted_config = {
#             TermCol.MG_B(key) + "@": TermCol.BL_UL(value)
#             for key, value in config["projects"].items()
#         }
#         max_key_length = max(len(key) for key in formatted_config.keys())

#         for key, value in formatted_config.items():
#             print(f"{key:<{max_key_length+2}} {TermCol.ARROW} {value}")
#         exit(0)

#     if len(sys.argv) == 2:
#         if sys.argv[1] not in config["projects"]:
#             print(f"Error: {sys.argv[1]} not found in configuration")
#             exit(-1)
#         if not os.path.exists(config["projects"][sys.argv[1]]):
#             print(f"Error: path to {sys.argv[1]} not found")
#             exit(-1)
#         pid = os.getppid()
#         os.chdir(config["projects"][sys.argv[1]])
#         os.system("$SHELL")
#         os.kill(pid, signal.SIGKILL)

#     if len(sys.argv) == 3:
#         print(
#             "Error: deleting projects is unsupported, please edit the configuration file"
#         )

#     if len(sys.argv) == 4:
#         project = sys.argv[2]
#         path = sys.argv[3]

#         if project in reserved:
#             print(f"Error: {project} is a reserved CLI argument")
#             exit(-1)

#         config["projects"][project] = path

#         # with open(config_path, "w") as f:
#         #     json.dump(config, f)
#         save_config(config)
