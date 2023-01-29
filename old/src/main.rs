use serde::{self, Deserialize};
use serde_json;
use std::io::{Error, Read};
use std::path::Path;
use std::process::Command;
use std::{env, fs};

use nix::{
    sys::signal::{kill, Signal},
    unistd::getppid,
};

#[derive(Clone, Debug, Deserialize)]
struct Config {
    projects: Vec<Project>,
}

#[derive(Clone, Debug, Deserialize)]
struct Project {
    name: String,
    path: String,
}

// a function that parses a json file and returns a result
fn load_config_json(path: &str) -> Result<Config, Error> {
    // read json file ~/.goto
    let mut file = fs::File::open(path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;

    // parse json file
    let v: Config = serde_json::from_str(&contents)?;
    Ok(v)
}

fn change_env_dir(path: &String) -> Result<(), Error> {
    let path = Path::new(path.as_str());
    env::set_current_dir(&path)?;

    Ok(())
}

fn spawn_shell_and_kill_parent() {
    let parent_pid = getppid();
    let shell = env::var("SHELL").unwrap_or_else(|_| String::from("bash"));

    let mut child_command = Command::new(shell);

    let mut child = match child_command.spawn() {
        Ok(child) => child,
        Err(e) => panic!("Could not start new shell: {}", e),
    };

    match kill(parent_pid, Signal::SIGKILL) {
        Ok(_) => println!("killed"),
        Err(e) => {
            println!("Could not kill parent shell: {}", e);
            child.kill().expect("Could not kill child shell");
        }
    }
}

fn main() {
    let args = env::args().collect::<Vec<String>>();
    let project: String;

    match args.len() {
        2 => {
            project = args[1].clone();
        }
        _ => {
            println!("Usage: goto <project_name>");
            std::process::exit(1);
        }
    }

    let config = match load_config_json(".goto.json") {
        Ok(v) => v,
        Err(e) => panic!("Error: {}", e),
    };

    println!("{:?}", config);

    let matches: Vec<Project> = config
        .clone()
        .projects
        .into_iter()
        .filter(|proj| proj.name == project)
        .collect();

    match matches.len() {
        0 => println!("No matches found"),
        1 => {
            let path = &matches[0].path;
            match change_env_dir(path) {
                Ok(_) => spawn_shell_and_kill_parent(),
                Err(e) => panic!("Error: {}", e),
            }
        }
        _ => println!("Unexpected error: check config file for duplicate keys"),
    }
}
