import requests

def get_team_names():
    """Fetch the team names from the FPL API."""
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    data = response.json()

    teams = {team['id']: team['name'] for team in data['teams']}
    return teams

def get_player_id(player_name):
    """Fetch the player ID from the FPL API based on the name."""
    url = f'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    data = response.json()

    players = data['elements']
    matching_players = []

    for player in players:
        if player_name.lower() in player['web_name'].lower():
            matching_players.append({
                'id': player['id'],
                'name': player['web_name'],
                'team': player['team'],
                'team_name': data['teams'][player['team'] - 1]['name']  # Fetching team name
            })

    return matching_players

def get_player_gameweek_data(player_id):
    """Fetch gameweek data for the player from the FPL API."""
    url = f'https://fantasy.premierleague.com/api/element-summary/{player_id}/'
    response = requests.get(url)
    data = response.json()

    return data['history']

def get_fixture_details(fixture_id, teams, player_team):
    """Fetch the fixture details to get opponent and home/away info."""
    url = f'https://fantasy.premierleague.com/api/fixtures/'
    response = requests.get(url)
    fixtures = response.json()

    for fixture in fixtures:
        if fixture['id'] == fixture_id:
            # Check if the player's team is playing at home or away
            if fixture['team_h'] == player_team:
                home_or_away = "H"
                opponent = fixture['team_a']
            else:
                home_or_away = "A"
                opponent = fixture['team_h']

            return teams[opponent], home_or_away

    return None, None

def display_player_performance(player_name):
    """Display the weekly performance of the player."""
    teams = get_team_names()  # Get the team names at the beginning
    matching_players = get_player_id(player_name)

    if not matching_players:
        print(f"Player '{player_name}' not found.")
        return

    if len(matching_players) > 1:
        print(f"Multiple players found with the name '{player_name}':")
        for i, player in enumerate(matching_players, 1):
            print(f"{i}. {player['name']} - {player['team_name']}")

        choice = int(input(f"Please select the correct player (1-{len(matching_players)}): "))
        player = matching_players[choice - 1]
    else:
        player = matching_players[0]

    print(f"Fetching data for {player['name']}...")
    gameweek_data = get_player_gameweek_data(player['id'])

    if not gameweek_data:
        print(f"No gameweek data found for {player['name']}.")
        return

    # Initialize stats counters for home and away
    total_goals_home = 0
    total_assists_home = 0
    total_clean_sheets_home = 0
    total_points_home = 0  # Track total home points

    total_goals_away = 0
    total_assists_away = 0
    total_clean_sheets_away = 0
    total_points_away = 0  # Track total away points

    total_goals = 0
    total_assists = 0
    total_clean_sheets = 0

    print(f"\n{player['name']}'s Weekly Performance:")
    for game in gameweek_data:
        fixture_id = game['fixture']
        goals = game['goals_scored']
        assists = game['assists']
        clean_sheets = game['clean_sheets']
        round_number = game['round']
        points = game['total_points']  # Points for the gameweek
        opponent, venue = get_fixture_details(fixture_id, teams, player['team'])

        if opponent:
            # Simplified output format with the requested changes
            print(f"GW{round_number}: {points}p, {goals}G, {assists}A, {clean_sheets}CS vs {opponent} ({venue})")

            # Accumulate overall points
            total_goals += goals
            total_assists += assists
            total_clean_sheets += clean_sheets

            # Accumulate stats for home and away games
            if venue == "H":
                total_goals_home += goals
                total_assists_home += assists
                total_clean_sheets_home += clean_sheets
                total_points_home += points
            else:
                total_goals_away += goals
                total_assists_away += assists
                total_clean_sheets_away += clean_sheets
                total_points_away += points

    # After displaying weekly points, show the totals for home and away stats
    print(f"\n{player['name']}'s Total Stats:")
    print(f"Total G: {total_goals}")
    print(f"Total A: {total_assists}")
    print(f"Total CS: {total_clean_sheets}")

    print(f"\nHome Stats:")
    print(f"Total Points: {total_points_home}")
    print(f"G: {total_goals_home}")
    print(f"A: {total_assists_home}")
    print(f"CS: {total_clean_sheets_home}")

    print(f"\nAway Stats:")
    print(f"Total Points: {total_points_away}")
    print(f"G: {total_goals_away}")
    print(f"A: {total_assists_away}")
    print(f"CS: {total_clean_sheets_away}")

def get_team_players(team_name):
    """Get all players of the team and display their total points."""
    teams = get_team_names()
    url = f'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    data = response.json()

    team_id = None
    for team in data['teams']:
        if team['name'].lower() == team_name.lower():
            team_id = team['id']
            break

    if not team_id:
        print(f"Team '{team_name}' not found.")
        return

    # Fetch all players in the team
    players = [player for player in data['elements'] if player['team'] == team_id]

    # Get total points for each player
    player_points = []

    for player in players:
        player_points.append({
            'name': player['web_name'],
            'total_points': player['total_points']
        })

    # Sort players by total points in descending order
    player_points.sort(key=lambda x: x['total_points'], reverse=True)

    print(f"\nTotal Points for All Players in {team_name}:")
    for player in player_points:
        print(f"{player['name']}: {player['total_points']} points")

def list_top_players_by_points_per_million():
    """Display the top 20 players by points per million for a specific position."""
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    data = response.json()

    # Position mapping based on FPL API
    position_map = {
        1: 'GK',
        2: 'DF',
        3: 'MF',
        4: 'ST'
    }

    # Ask the user for a position
    print("Select a position to search:")
    print("1. Goalkeeper (GK)")
    print("2. Defender (DF)")
    print("3. Midfielder (MF)")
    print("4. Forward (ST)")

    position_choice = int(input("Enter your choice (1, 2, 3, or 4): "))
    if position_choice not in position_map:
        print("Invalid choice. Please select a valid position.")
        return

    selected_position = position_map[position_choice]
    print(f"\nFetching top 20 players for position: {selected_position}...")

    players = data['elements']
    players_ppm = []

    for player in players:
        if player['element_type'] == position_choice:  # Match position type
            total_points = player['total_points']
            value = player['now_cost'] / 10  # Convert value to millions
            if value > 0:  # Avoid division by zero
                ppm = total_points / value
                players_ppm.append({
                    'name': player['web_name'],
                    'team': data['teams'][player['team'] - 1]['name'],
                    'position': selected_position,
                    'total_points': total_points,
                    'value': value,
                    'ppm': ppm
                })

    # Sort by PPM in descending order
    players_ppm.sort(key=lambda x: x['ppm'], reverse=True)

    # Display the top 20 players
    print(f"\nTop 20 Players by Points Per Million in Position: {selected_position}")
    for i, player in enumerate(players_ppm[:20], 1):
        print(f"{i}. {player['name']} ({player['team']}) - {player['total_points']} points, "
              f"{player['value']}m, {player['ppm']:.2f} PPM")


def main():
    """Main function to ask the user for a player name or team name."""
    while True:
        print("\nChoose an option:")
        print("1. Search for a player by name")
        print("2. View total points for all players of a team")
        print("3. View top 20 players by points per million")
        print("4. Exit")

        choice = int(input("Enter your choice (1, 2, 3, or 4): "))

        if choice == 1:
            player_name = input("Enter the player's name you want to search: ")
            display_player_performance(player_name)
        elif choice == 2:
            team_name = input("Enter the team name you want to search: ")
            get_team_players(team_name)
        elif choice == 3:
            list_top_players_by_points_per_million()
        elif choice == 4:
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
