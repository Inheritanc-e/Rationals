# Rationals Bot

This project is a Discord bot specifically for use with the The Rationals Discord. It provides numerous utilities and other tools to help keep `The Rationals` discord server running like a beast.

## Discord Setup

To get a **token**, go to [Discord Developer Portal](https://discord.com/developers/applications). Create an application and add a bot.

## Dev Installation

1. Traditional way: `git clone https://github.com/gurkult/gurkbot.git` or `git clone git@github.com:gurkult/gurkbot.git`.
   Using Github CLI: `gh repo clone gurkult/gurkbot`. Then navigate to the directory `cd gurkbot/`
2. Create a new branch by `git checkout -b <name of new local branch> main` or `git switch -c <name of new local branch> main`. Make sure the new branch name is related to the feature or the fix you have in mind.
3. Create a guild and save its id. 

4. Create a `.env` file with following contents:

   ```text
   TOKEN = <Your token> # See Discord Setup above
   PREFIX = "!" # the prefix the bot should use, will default to "!" if this is not present
   Guild_Id = <Your guild id>
   ```

5. Install pipenv: `pip install pipenv` and run the following:

   ```sh
   # This will install the development and project dependencies.
   pipenv sync --dev

   # This will install the pre-commit hooks.
   pipenv run precommit

   # Optionally: run pre-commit hooks to initialize them.
   # You can start working on the feature after this.
   pipenv run pre-commit run --all-files
   
   # Run the bot
   pipenv run start

   ```

6. Testin on a server. If Auto_Config in `config-list.yaml` is True then the bot will create the required channels and roles in the server. If it is set to False then you will have to run the `|setup` command in your server to create the roles and channels and sync their ids with the config file.

7. Lint and format your code properly (use black or flake8) or `pipenv run lint`, and push changes `git push -u origin <name of new remote branch>`
