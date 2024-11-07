# Tiny URL POC

## Execution Steps

1. Ensure `Python` is installed and set up on your system.
2. Open a terminal/bash window and navigate to the `tiny-url` project directory.
3. Execute the command `python -m venv tiny-env` to create the Virtual Environment.
4. Activate the Virtual Environment with the command `source tiny-env/bin/activate`.
5. Set up necessary libraries and dependencies with the command `tiny-env/bin/pip install -r requirements.txt`.

### Run as Command Line Interactive Shell

##### Python + Cmd + SQLite + SQLAlchemy

- Execute the command `python start_sim.py`
  - Descriptions and help for all commands are present within the simulation by following the prompts.
  - A persistent version of the simulation may be ran by specifying a database name as a command line argument such as `python start_sim.py -n turl` or `python start_sim.py --name turl`.
  - The Root Domain of the simulation may be controlled by specifying a command line argument such as `python start_sim.py -d turl.com` or `python start_sim.py --domain turl.com`

### Run as Web Application

##### Python + Flask + SQLite + SQLAlchemy

1. Ensure all necessary application variables (ie: `SQLALCHEMY_DATABASE_URI` and `BASE_DOMAIN`) are set in `web/config.json`.
2. Initialize Database Tables by running `python setup.py`.
3. Start the application by running `python start.py`.

#### Testing Steps

- Execute the command `python -m pytest -v`
  - This will run all methods in the `tests` directory and any subdirectories, using the configured Flask fixture and test client.
