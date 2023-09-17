import yaml

with open("constants.yaml", "r") as f:
    constants = yaml.safe_load(f)

POS_ID_TO_NAME = {k + 1: v for k, v in enumerate(constants["pos"])}
POS_NAME_TO_ID = {v: k + 1 for k, v in enumerate(constants["pos"])}

TEAMS_ID_TO_NAME = {k + 1: v for k, v in enumerate(constants["teams"])}
TEAMS_NAME_TO_ID = {v: k + 1 for k, v in enumerate(constants["teams"])}

TEAM_FULL_NAME_TO_ABBR = {
    "Arsenal": "ARS",
    "Aston Villa": "AVL",
    "Bournemouth": "BOU",
    "Brentford": "BRE",
    "Brighton": "BHA",
    "Burnley": "BUR",
    "Chelsea": "CHE",
    "Crystal Palace": "CRY",
    "Everton": "EVE",
    "Fulham": "FUL",
    "Liverpool": "LIV",
    "Luton": "LUT",
    "Man City": "MCI",
    "Man Utd": "MUN",
    "Newcastle": "NEW",
    "Nott'm Forest": "NFO",
    "Sheffield Utd": "SHU",
    "Spurs": "TOT",
    "West Ham": "WHU",
    "Wolves": "WOL"
}