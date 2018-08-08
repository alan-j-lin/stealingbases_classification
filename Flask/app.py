from flask import Flask, render_template, jsonify, request, abort
from api import make_prediction, ER_delta, stats_pull
import numpy as np

# Initialization of the Baseball App
app = Flask('BaseballApp')

@app.route('/test')
def do_test():
    return render_template('nav_tutorial.html')

# Homepage of app will just return baseball html template
@app.route('/')
def renderbasehtml():
    return render_template('baseball.html', hitter = 'default', pitcher = 'default')

# Post method for predictions
@app.route('/predict', methods = ['POST'])
def do_prediction():

    # check to see if what is being passed is a JSON
    if not request.json:
        abort(400)
    # check to see that the necessary entries are in the JSON
    elif (('Pitcher' not in request.json) or ('Hitter' not in request.json) or
        ('is_rob1' not in request.json) or ('is_rob2' not in request.json) or
        ('is_rob3' not in request.json) or ('startingouts' not in request.json)):
        abort(400)

    # using make_prediction function from api return the prediction dictionary
    data = request.json
    response = make_prediction(data)

    differential = ER_delta((data['startingouts'], data['is_rob1'], data['is_rob2'],
                        data['is_rob3']), response['prediction'])

    if type(differential) == str:
        response['ER_delta'] = differential
    else:
        response['ER_delta'] = float(np.round(differential, 4))

    return jsonify(response)

@app.route('/stats', methods = ['POST'])
def fetch_stats():

    # check to see if what is being passed is a JSON
    if not request.json:
        abort(400)
    # check to see that the necessary entries are in the JSON
    elif (('Player' not in request.json) or ('Pos' not in request.json)):
        abort(400)

    # using stats_pull from api return the details dictionary
    details = request.json
    response = stats_pull(details)

    return jsonify(response)



# Running Baseball App with debug mode turned on
app.run(debug=True)
