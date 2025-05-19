import requests
from itertools import combinations
from datetime import datetime


# Step 1: Fetch fixture data from FPL API
def get_favorable_fixtures():
    url = "https://fantasy.premierleague.com/api/fixtures/"
    response = requests.get(url)
    response.raise_for_status()
    fixtures = response.json()

    # Map teams to gameweeks with fixture difficulty 2
    favorable_fixtures = {}
    for fixture in fixtures:
        home_team = fixture['team_h']
        away_team = fixture['team_a']
        gameweek = fixture['event']
        home_difficulty = fixture['team_h_difficulty']
        away_difficulty = fixture['team_a_difficulty']

        if home_difficulty == 2:
            favorable_fixtures.setdefault(home_team, []).append(gameweek)
        if away_difficulty == 2:
            favorable_fixtures.setdefault(away_team, []).append(gameweek)

    return favorable_fixtures, fixtures  # Also return all fixtures for later use


# Step 2: Fetch the current gameweek
def get_current_gameweek():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    for event in data['events']:
        if event['is_current']:
            return event['id']
    return None  # Return None if no current gameweek is found (unlikely)


# Step 3: Convert team IDs to team names
def get_team_mapping():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return {team['id']: team['name'] for team in data['teams']}


# Step 4: Find top 10 longest consecutive blocks
def find_top_longest_blocks(fixture_dict, team_mapping, max_teams, start_gameweek):
    """
    Find the top 10 longest consecutive gameweeks blocks using up to max_teams,
    starting from a specific gameweek.
    """
    team_ids = list(fixture_dict.keys())
    results = []

    # Iterate through all combinations of up to max_teams
    for r in range(1, max_teams + 1):
        for team_combo in combinations(team_ids, r):
            # Combine gameweeks from the selected teams
            combined_gameweeks = set()
            for team in team_combo:
                combined_gameweeks.update(week for week in fixture_dict.get(team, []) if week >= start_gameweek)
            combined_gameweeks = sorted(combined_gameweeks)

            # Find the longest consecutive block for this combination
            current_block = [combined_gameweeks[0]] if combined_gameweeks else []
            for i in range(1, len(combined_gameweeks)):
                if combined_gameweeks[i] == combined_gameweeks[i - 1] + 1:
                    current_block.append(combined_gameweeks[i])
                else:
                    if len(current_block) > 1:  # Store only blocks with length > 1
                        results.append((current_block, team_combo))
                    current_block = [combined_gameweeks[i]]

            # Final check for the last block
            if len(current_block) > 1:
                results.append((current_block, team_combo))

    # Sort results by block length in descending order
    results = sorted(results, key=lambda x: len(x[0]), reverse=True)

    # Map team IDs to names and limit to top 10
    top_10 = []
    for block, teams in results[:10]:
        team_names = [team_mapping[team_id] for team_id in teams]
        top_10.append((block, team_names))

    return top_10


# Step 5: Print fixtures used in the top 10 longest consecutive blocks
def print_fixtures_for_blocks(top_10_blocks, all_fixtures, team_mapping):
    print(f"\nTop 10 Longest Consecutive Gameweeks:\n")
    for i, (block, teams) in enumerate(top_10_blocks, start=1):
        block_str = '-'.join(map(str, block))
        print(f"{i}. Gameweeks: {block_str}")
        print(f"   Total Length: {len(block)}")
        print(f"   Teams: {', '.join(teams)}")

        # Now, print the fixtures involved in these consecutive gameweeks
        print("   Fixtures used in these gameweeks:")
        for gameweek in block:
            for fixture in all_fixtures:
                if fixture['event'] == gameweek:
                    home_team_name = team_mapping[fixture['team_h']]
                    away_team_name = team_mapping[fixture['team_a']]

                    # Check if the fixture has a difficulty rating of 2 for either team
                    home_difficulty = fixture['team_h_difficulty']
                    away_difficulty = fixture['team_a_difficulty']

                    # Only print fixtures with difficulty 2 for the teams in the block
                    if (home_team_name in teams and home_difficulty == 2) or (
                            away_team_name in teams and away_difficulty == 2):
                        print(f"     Gameweek {gameweek}: {home_team_name} vs {away_team_name}")
        print()


# Main Execution
if __name__ == "__main__":
    # Fetch data
    favorable_fixtures, all_fixtures = get_favorable_fixtures()
    team_mapping = get_team_mapping()
    current_gameweek = get_current_gameweek()

    if current_gameweek is None:
        print("Could not determine the current gameweek.")
    else:
        # Ask the user for the maximum number of teams
        try:
            max_teams = int(input(
                "Enter the maximum number of teams to use for consecutive gameweeks calculation (e.g., 1, 2, 3): "))
            if max_teams < 1 or max_teams > len(favorable_fixtures):
                raise ValueError(f"The number of teams must be between 1 and {len(favorable_fixtures)}.")
        except ValueError as e:
            print(f"Invalid input: {e}")
            exit(1)

        # Create a dictionary to map team IDs to favorable gameweeks
        fixture_dict = {team_id: set(gameweeks) for team_id, gameweeks in favorable_fixtures.items()}

        # Find the top 10 longest blocks with user-defined maximum teams, starting from the next gameweek
        top_10_blocks = find_top_longest_blocks(fixture_dict, team_mapping, max_teams=max_teams,
                                                start_gameweek=current_gameweek + 1)

        # Display the results and the fixtures used
        print_fixtures_for_blocks(top_10_blocks, all_fixtures, team_mapping)
