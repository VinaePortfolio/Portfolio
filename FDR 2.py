import requests
from itertools import combinations

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
            favorable_fixtures.setdefault(home_team, []).append((gameweek, home_team, away_team, "home"))
        if away_difficulty == 2:
            favorable_fixtures.setdefault(away_team, []).append((gameweek, home_team, away_team, "away"))

    return favorable_fixtures, fixtures

# Step 2: Fetch the current gameweek
def get_current_gameweek():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    for event in data['events']:
        if event['is_current']:
            return event['id']
    return None

# Step 3: Convert team IDs to team names
def get_team_mapping():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return {team['id']: team['name'] for team in data['teams']}

# Step 4: Find top combinations maximizing fixture coverage with detailed listing
def find_top_fixture_coverage(fixture_dict, team_mapping, max_teams, start_gameweek):
    """
    Find the combinations of up to max_teams that maximize the number of gameweeks
    with fixtures rated 2 for the remaining season. Also, provide detailed fixture listings.
    """
    total_gameweeks = 38  # Premier League typically has 38 gameweeks
    team_ids = list(fixture_dict.keys())
    results = []

    # Iterate through all combinations of up to max_teams
    for r in range(1, max_teams + 1):
        for team_combo in combinations(team_ids, r):
            # Collect all favorable fixtures for this team combination
            combined_fixtures = {}
            for team in team_combo:
                for fixture in fixture_dict.get(team, []):
                    gameweek = fixture[0]
                    if gameweek >= start_gameweek:
                        combined_fixtures.setdefault(gameweek, []).append(fixture)

            # Create a gameweek coverage table
            coverage = []
            for gw in range(start_gameweek, total_gameweeks + 1):
                fixtures_in_gw = combined_fixtures.get(gw, [])
                if len(fixtures_in_gw) == 2:
                    coverage.append("✓✓")
                elif len(fixtures_in_gw) == 1:
                    coverage.append("✓")
                else:
                    coverage.append("✗")

            # Store the total count, the team combo, detailed fixtures, and coverage table
            results.append((sum(len(fixtures) for fixtures in combined_fixtures.values()),
                            team_combo, combined_fixtures, coverage))

    # Sort results by the total count of gameweeks with fixtures rated 2, in descending order
    results = sorted(results, key=lambda x: x[0], reverse=True)

    # Map team IDs to names and limit to top 10
    top_10 = []
    for count, teams, combined_fixtures, coverage in results[:10]:
        team_names = [team_mapping[team_id] for team_id in teams]
        top_10.append((count, team_names, combined_fixtures, coverage))

    return top_10

def get_consecutive_gameweek_ranges(coverage, start_gameweek):
    """
    Converts a list of gameweek coverage into a readable string of ranges and discrete weeks.
    E.g., coverage: ['✓', '✗', '✓', '✓', '✗', '✓✓']
    Gameweeks start from `start_gameweek` as provided.
    Returns: "GW12-GW15, GW17, GW19-GW20"
    """
    ranges = []
    start, end = None, None
    for i, cell in enumerate(coverage, start=start_gameweek):
        if cell != '✗':
            if start is None:
                start = i
            end = i
        elif start is not None:
            if start == end:
                ranges.append(f"GW{start}")
            else:
                ranges.append(f"GW{start}-GW{end}")
            start, end = None, None
    if start is not None:
        if start == end:
            ranges.append(f"GW{start}")
        else:
            ranges.append(f"GW{start}-GW{end}")
    return ", ".join(ranges)

def print_top_combinations_with_table(top_10_combinations, team_mapping, start_gameweek):
    print(f"\nTop Combinations for Fixture Rotation:\n")
    for i, (count, teams, combined_fixtures, coverage) in enumerate(top_10_combinations, start=1):
        print(f"{i}. Total Fixtures Rated 2: {count}")
        print(f"   Teams: {', '.join(teams)}")

        # Calculate consecutive gameweek ranges
        coverage_ranges = get_consecutive_gameweek_ranges(coverage, start_gameweek)
        print(f"   Gameweek Coverage Ranges: {coverage_ranges}")

        # Coverage Table Section
        print("\n   Coverage Table:")
        total_gameweeks = 38  # Fixed total gameweeks

        # Format headers and coverage rows with proper alignment
        gameweeks = range(start_gameweek, total_gameweeks + 1)
        header = "   GW: " + " ".join(f"{gw:>3}" for gw in gameweeks)
        row = "   Row:" + " ".join(f"{cell:>3}" for cell in coverage)

        print(header)
        print(row)

        # Detailed Fixtures Section
        print(f"\n   Detailed Fixtures:")
        for gameweek, fixtures in sorted(combined_fixtures.items()):
            print(f"     Gameweek {gameweek}:")
            for fixture in fixtures:
                gameweek, home_team, away_team, location = fixture
                home_team_name = team_mapping[home_team]
                away_team_name = team_mapping[away_team]
                location_label = "(H)" if location == "home" else "(A)"  # Simplified label
                print(f"       {home_team_name} vs {away_team_name} {location_label}")


# Main Execution
if __name__ == "__main__":
    # Fetch data
    favorable_fixtures, _ = get_favorable_fixtures()
    team_mapping = get_team_mapping()
    current_gameweek = get_current_gameweek()

    if current_gameweek is None:
        print("Could not determine the current gameweek.")
    else:
        # Ask the user for the maximum number of teams
        try:
            max_teams = int(input(
                "Enter the maximum number of teams to use for fixture rotation calculation (e.g., 1, 2, 3): "))
            if max_teams < 1 or max_teams > len(favorable_fixtures):
                raise ValueError(f"The number of teams must be between 1 and {len(favorable_fixtures)}.")
        except ValueError as e:
            print(f"Invalid input: {e}")
            exit(1)

        # Create a dictionary to map team IDs to favorable gameweeks and fixtures
        fixture_dict = {team_id: gameweeks for team_id, gameweeks in favorable_fixtures.items()}

        # Find the top combinations maximizing fixture coverage
        top_10_combinations = find_top_fixture_coverage(fixture_dict, team_mapping, max_teams=max_teams,
                                                        start_gameweek=current_gameweek + 1)

        # Display the results
        print_top_combinations_with_table(top_10_combinations, team_mapping,
                                          start_gameweek=current_gameweek + 1)
