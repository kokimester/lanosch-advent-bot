# lanosch-advent-bot
This is a Discord bot which posts daily messages during the pre-Christmas "Advent" time.
It uses a database of game keys and dates in JSON to know when to post which keys.
You can define the channels and roles you want to use in the .env file along with your token.
Additional utilities are present to help prepare the database for use, such as steam URL scraper, csv-to-json converter etc.
If you have any suggestions, open an issue, a pull request, or contact the maintainer on Discord.

Disclaimer: some of the scripts were vibecoded, so beware :D

## Usage

1) To run the bot, prepare an input-advent.json file in the correct format. You can verify the format by running validate-input.py (will be integrated into the bot itself later).
2) Populate your .env file using the provided .env.example file.
3) Run `pipenv install` to install the dependencies.
4) Run `pipenv run python3 advent-bot.py` to start the bot.

Additionally, if you plan on using this bot on a server you can start it using the provided bash script.
To start it on restart, add it to a crontab entry using screen:
`@reboot screen -dmS adventbot bash -c 'cd /path/to/repo/ && bash run-advent-bot.sh >> /path/to/log/advent-bot.log'`
