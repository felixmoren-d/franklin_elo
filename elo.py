import pandas as pd
import math
from collections import defaultdict
import os

class EloRatingSystem:
    def __init__(self, initial_rating=1000, k_factor=32):
        self.initial_rating = initial_rating
        self.k_factor = k_factor
        self.player_ratings = defaultdict(lambda: self.initial_rating)
        self.game_results = []

    def load_initial_ratings(self, ratings_file):
        """Load initial player ratings from an Excel file."""
        ratings_df = pd.read_excel(ratings_file, index_col=0).transpose()
        for player, rating in ratings_df.items():
            self.player_ratings[player] = rating.values[0]
        print("Loaded initial player ratings.")

    def calculate_expected_score(self, team1_avg, team2_avg):
        """Calculate the expected score for Team 1 based on ELO ratings."""
        return 1 / (1 + 10 ** ((team2_avg - team1_avg) / 400))

    def update_ratings(self, team1, team2, score1, score2):
        """Update the ratings for players based on game outcome."""
        # Calculate team average ratings
        team1_avg = sum(self.player_ratings[player] for player in team1) / len(team1)
        team2_avg = sum(self.player_ratings[player] for player in team2) / len(team2)

        # Expected scores
        expected_team1 = self.calculate_expected_score(team1_avg, team2_avg)
        actual_team1 = 1 if score1 > score2 else 0 if score1 < score2 else 0.5

        # Rating change for teams
        rating_change = self.k_factor * (actual_team1 - expected_team1)

        # Update ratings for each player
        for player in team1:
            self.player_ratings[player] += rating_change / len(team1)
        for player in team2:
            self.player_ratings[player] -= rating_change / len(team2)

        # Save game results
        self.game_results.append({
            'Team1': ', '.join(team1),
            'Team2': ', '.join(team2),
            'Score1': score1,
            'Score2': score2,
            'Team1_Avg_Rating': team1_avg,
            'Team2_Avg_Rating': team2_avg,
            'Expected_Team1': expected_team1,
            'Actual_Team1': actual_team1,
            'Rating_Change': rating_change
        })

    def process_games(self, input_file, output_file):
        """Process games from an Excel file and update ratings."""
        # Read input file in column format
        df = pd.read_excel(input_file)

        for index in range(len(df)):
            # Parse team players
            team1 = [p.strip() for p in df['Team1'][index].split(',')]
            team2 = [p.strip() for p in df['Team2'][index].split(',')]
            
            # Get scores
            score1 = df['Score1'][index]
            score2 = df['Score2'][index]          
            # Update ratings
            self.update_ratings(team1, team2, score1, score2)
            print(f"Processed Game {index + 1}: Team1={team1}, Team2={team2}, Score1={score1}, Score2={score2}")
        
        # Save updated ratings to file
        self.save_ratings(output_file)

    def save_game_results(self, output_file):
        """Save detailed game results to an Excel file, appending if the file exists."""
        game_results_df = pd.DataFrame(self.game_results)
        if os.path.exists(output_file):
            # Read the existing file and append
            existing_df = pd.read_excel(output_file)
            game_results_df = pd.concat([existing_df, game_results_df], ignore_index=True)
            print("Appending to existing game results file.")
        else:
            print("Creating new game results file.")
        game_results_df.to_excel(output_file, index=False)
        print(f"Game results saved to {output_file}")

    def save_ratings(self, output_file):
        """Save player ELO scores to an Excel file."""
        ratings_df = pd.DataFrame(self.player_ratings.items(), columns=['Player', 'Rating'])
        print(ratings_df.head())

        ratings_df.to_excel(output_file, index=False)
        print(f"Player ELO scores saved to {output_file}")

# Example usage
if __name__ == "__main__":
    input_file = "game.xlsx"  # Input Excel file path
    ratings_input_file = "elo.xlsx"  # Input Excel file for initial ratings
    ratings_output_file = "elo.xlsx"  # Output file path for ratings
    game_results_output_file = "game_results_output.xlsx"  # Output file for game results

    elo_system = EloRatingSystem()
    elo_system.load_initial_ratings(ratings_input_file)
    elo_system.process_games(input_file, ratings_output_file)
    elo_system.save_game_results(game_results_output_file)
    elo_system.save_ratings("elo.xlsx")
