#!/bin/bash

# aaa.sh - A CLI tool to manage Airflow setup tasks

# Default Airflow home directory
DEFAULT_AIRFLOW_HOME=~/sandbox/toys/airflow

# Function to check if script is sourced
is_sourced() {
    [[ "$BASH_SOURCE" != "$0" ]] && return 0 || return 1
}

# Function to display help message
usage() {
    cat << EOF
Usage: $(basename "$0") [options]

Options:
  -a, --admin-user    Create an admin user for Airflow
  -e, --env-home      Set the AIRFLOW_HOME environment variable
  -d, --db            Initialize the Airflow database
  -x, --remove-ex     Remove Airflow example DAGs
  -h, --help          Show this help message

Examples:
  source ./$(basename "$0") -e
      Sets AIRFLOW_HOME to $DEFAULT_AIRFLOW_HOME.

  ./$(basename "$0") -d
      Runs 'airflow db migrate' to initialize the Airflow database.

  ./$(basename "$0") --admin-user
      Creates an admin user with username 'admin', password 'admin'.

  ./$(basename "$0") -x
      Removes the example DAGs from the Airflow installation.

  source ./$(basename "$0") -e -d -a
      Sets AIRFLOW_HOME, initializes the database, and creates an admin user.

EOF
    is_sourced && return 0 || exit 0
}

# Function to check if Airflow is installed
check_airflow() {
    if ! command -v airflow >/dev/null 2>&1; then
        echo "Error: Airflow is not installed or not found in PATH."
        is_sourced && return 1 || exit 1
    fi
}

# Function to set AIRFLOW_HOME
set_airflow_home() {
    export AIRFLOW_HOME="$DEFAULT_AIRFLOW_HOME"
    echo "AIRFLOW_HOME set to $AIRFLOW_HOME"
    mkdir -p "$AIRFLOW_HOME" || {
        echo "Error: Failed to create AIRFLOW_HOME directory."
        is_sourced && return 1 || exit 1
    }
}

# Function to initialize the database
init_database() {
    check_airflow
    airflow db migrate || {
        echo "Error: Failed to initialize Airflow database."
        is_sourced && return 1 || exit 1
    }
    echo "Airflow database initialized."
}

# Function to create admin user
create_admin_user() {
    check_airflow
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --email admin@example.com \
        --role Admin \
        --password admin || {
            echo "Error: Failed to create admin user."
            is_sourced && return 1 || exit 1
        }
    echo "Admin user created with username: admin and password: admin"
}

# Function to remove example DAGs
remove_example_dags() {
    local example_dags_path
    example_dags_path=$(python -c "import airflow; print(airflow.__path__[0])" 2>/dev/null)/example_dags
    if [ -d "$example_dags_path" ]; then
        rm -rf "$example_dags_path" || {
            echo "Error: Failed to remove example DAGs."
            is_sourced && return 1 || exit 1
        }
        echo "Example DAGs removed from $example_dags_path."
    else
        echo "Warning: Example DAGs directory not found at $example_dags_path."
    fi
}

# Initialize flags
admin_user=false
env_home=false
db=false
remove_ex=false

# Reset OPTIND for getopts
OPTIND=1

# Check for no arguments
if [ $# -eq 0 ]; then
    echo "Error: No options provided."
    echo "Use '$(basename "$0") -h' for help."
    is_sourced && return 1 || exit 1
fi

# Debug: Print arguments received
# echo "Arguments: $@" >&2

# Process short flags using getopts
while getopts "aedxh" opt; do
    case $opt in
        a) admin_user=true ;;
        e) env_home=true ;;
        d) db=true ;;
        x) remove_ex=true ;;
        h) usage ;;
        \?) echo "Error: Invalid option -$OPTARG." >&2
            echo "Use '$(basename "$0") -h' for help." >&2
            is_sourced && return 1 || exit 1 ;;
    esac
done

# Shift past the options processed by getopts
shift $((OPTIND - 1))

# Process long flags
while [ $# -gt 0 ]; do
    case "$1" in
        --admin-user) admin_user=true ;;
        --env-home) env_home=true ;;
        --db) db=true ;;
        --remove-ex) remove_ex=true ;;
        --help) usage ;;
        *) echo "Error: Unknown option '$1'." >&2
           echo "Use '$(basename "$0") -h' for help." >&2
           is_sourced && return 1 || exit 1 ;;
    esac
    shift
done

# Debug: Print flag states
# echo "Flags: admin_user=$admin_user, env_home=$env_home, db=$db, remove_ex=$remove_ex" >&2

# Check if at least one action was specified
if ! $admin_user && ! $env_home && ! $db && ! $remove_ex; then
    echo "Error: No valid actions specified."
    echo "Use '$(basename "$0") -h' for help."
    is_sourced && return 1 || exit 1
fi

# Execute the requested actions
$env_home && set_airflow_home
$db && init_database
$admin_user && create_admin_user
$remove_ex && remove_example_dags