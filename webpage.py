from flask import Flask, render_template, request, redirect, url_for, session
from elo_calc.elo import EloRatingSystem

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy credentials
USERNAME = "mikem"
PASSWORD = "hotdog"

rankings = EloRatingSystem()
try: 
    rankings.load_initial_ratings('elo_calc/player_ratings.csv')
except:
    pass




@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True

            return redirect(url_for('team_input'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/team_input', methods=['GET', 'POST'])
def team_input():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        games = []
        for i in range(len(request.form.getlist('team1_players'))):
            team1_players = request.form.getlist('team1_players')[i]
            team2_players = request.form.getlist('team2_players')[i]
            team1_score = request.form.getlist('team1_score')[i]
            team2_score = request.form.getlist('team2_score')[i]


            games.append({
                'Team1': team1_players.split(','),
                'Team2': team2_players.split(','),
                'Score1': int(team1_score),
                'Score2': int(team2_score)
            })

        rankings.input_games(games)
        rankings.save_game_results('elo_calc/game_results.csv')
        rankings.save_ratings('elo_calc/player_ratings.csv')

        return render_template('team_input.html', player_rankings=rankings.return_ratings())


    return render_template('team_input.html', player_rankings=rankings.return_ratings())

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
