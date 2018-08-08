import numpy as np
import pandas as pd
import pickle

# loading pickle files from the model folder
pipeline = pickle.load(open('./model/basestealing_model.pkl', 'rb'))
hitterpkl = pickle.load(open('./model/hitter_input.pkl', 'rb'))
pitcherpkl = pickle.load(open('./model/pitcher_input.pkl', 'rb'))

# establishing hitter and pitcher dfs, easier to find entries by setting index to name
hitter_df = hitterpkl.set_index('Name')
pitcher_df = pitcherpkl.set_index('Name')

# list of columns used by model prediction
X_cols = ['startingouts', 'CTv', 'CB_per', 'CH_per', 'CHv', 'bc_CTv', 'bc_CH_per',
       'bc_SF_per', 'bc_SFv', 'o_swing_per', 'o_contact_per', 'contact_per',
       'f_strike_per', 'bc_o_swing_per', 'bc_z_swing_per', 'bc_swing_per',
       'bc_z_contact_per', 'bc_contact_per', 'bc_zone_per', 'bc_f_strike_per',
       'is_pitcherR', 'is_rob1', 'is_rob2']

# columns from each df that will be used in the model prediction
# data will be accessed by hitter and batter name
pitcher_cols = ['CTv', 'CB_per', 'CH_per', 'CHv', 'bc_CTv','bc_CH_per',
            'bc_SF_per', 'bc_SFv', 'is_pitcherR']

hitter_cols = ['o_swing_per', 'o_contact_per', 'contact_per', 'f_strike_per',
            'bc_o_swing_per', 'bc_z_swing_per', 'bc_swing_per','bc_z_contact_per',
            'bc_contact_per', 'bc_zone_per', 'bc_f_strike_per']

# example used in the prediction call if nothing is assigned
example = {
    'Pitcher': 'Aroldis Chapman', #str
    'Hitter': 'Jose Urena', #str
    'is_rob1': 1, #int
    'is_rob2': 0, #int
    'startingouts': 0, #int
}

# base stealing model prediction function
def make_prediction(features):

    # get the name of the pitcher and hitter
    pitcher_name = features['Pitcher']
    hitter_name = features['Hitter']

    # check to see if both the pitcher and hitter names are contained in the dfs
    if pitcher_name in pitcher_df.index and hitter_name in hitter_df.index:

        #finds the entry for the pitcher specified by features
        pitcher_entry = pitcher_df.loc[pitcher_name]
        pitcher_vals = pitcher_entry[pitcher_cols].values.reshape(-1,1)
        #finds the entry of hitter specific by features
        hitter_entry = hitter_df.loc[hitter_name]
        hitter_vals = hitter_entry[hitter_cols].values.reshape(-1,1)

        #values that will be used in the array in the prediction
        startingouts_val = np.array(features['startingouts']).reshape(-1, 1)
        pitch_stats = pitcher_vals[:-1]
        hitter_stats = hitter_vals
        pitcher_hand = np.array(pitcher_vals[-1]).reshape(-1,1)
        rob1_val = np.array(features['is_rob1']).reshape(-1, 1)
        rob2_val = np.array(features['is_rob2']).reshape(-1, 1)

        # array that will be used to make the prediction
        X = np.concatenate([startingouts_val, pitch_stats, hitter_stats,
                            pitcher_hand, rob1_val, rob2_val]).reshape(1,-1)

        # probability of the model prediction
        prob_steal = pipeline.predict_proba(X)[0, 1]

        # dictionary that will be returned as the output from the model
        result = {
            'prediction': int(prob_steal >= 0.5),
            'prob_steal': f'{np.round(prob_steal, 3) * 100}%'
        }

    # check if pitcher name is the one that is missing
    elif pitcher_name not in pitcher_df.index:
        result = {
            'prediction': 'Incorrect pitcher name',
            'prob_steal': 'Error'
        }
    # if pitcher name is there then hitter name is the one that is missing
    else:
        result = {
            'prediction': 'Incorrect hitter name',
            'prob_steal': 'Error'
        }

    return result


# function to look up the expected run based on the game situation
def ER_value(n_outs, is_b1, is_b2, is_b3):
    # dictionary of all of the expected run values (# of outs, rob1, rob2, rob3)
    expected_runs = {
        (0, 0, 0, 0): 0.49,
        (0, 1, 0, 0): 0.88,
        (0, 0, 1, 0): 1.13,
        (0, 1, 1, 0): 1.50,
        (0, 0, 0, 1): 1.37,
        (0, 1, 0, 1): 1.75,
        (0, 0, 1, 1): 1.98,
        (0, 1, 1, 1): 2.37,
        (1, 0, 0, 0): 0.26,
        (1, 1, 0, 0): 0.52,
        (1, 0, 1, 0): 0.69,
        (1, 1, 1, 0): 0.92,
        (1, 0, 0, 1): 0.96,
        (1, 1, 0, 1): 1.17,
        (1, 0, 1, 1): 1.40,
        (1, 1, 1, 1): 1.57,
        (2, 0, 0, 0): 0.10,
        (2, 1, 0, 0): 0.23,
        (2, 0, 1, 0): 0.33,
        (2, 1, 1, 0): 0.44,
        (2, 0, 0, 1): 0.38,
        (2, 1, 0, 1): 0.50,
        (2, 0, 1, 1): 0.61,
        (2, 1, 1, 1): 0.76
    }
    return expected_runs[(n_outs, is_b1, is_b2, is_b3)]

# function to calculate the estimated difference in the expected run value after the steal attempt
def ER_delta(ER_tup, steal_pred):

    # constants from the expected run parameter tuple
    n_outs = float(ER_tup[0])
    b1 = float(ER_tup[1])
    b2 = float(ER_tup[2])
    b3 = float(ER_tup[3])

    # condition if steal_pred is actually an error message
    if type(steal_pred) != int:
        return 'Error'
    # condition if the steal attempt fails
    elif steal_pred == 0:
        # inning is over if outs is at 2, so expected run becomes zero.
        if n_outs == 2:
            return 'Inning Over'
        # add one to the outs if caught stealing, can't determine exactly which runner is caught
        else:
            return float(ER_value(n_outs + 1, b1, b2, b3) - ER_value(n_outs, b1, b2, b3))

    # steal attempt succeeds
    else:
        # all baserunners shift values over by 1
        new_b1 = 0
        new_b2 = b1
        new_b3 = b2

        # exception to above case as only first base is likely to steal on this instance
        if (b3 == 1) and (b2 == 0) and (b1 == 1):
            new_b3 = 1
            return float(ER_value(n_outs, new_b1, new_b2, new_b3) - ER_value(n_outs, b1, b2, b3))
        # if runner is on 3rd base and succesfully steals, run is scored so return that instead of number
        elif b3 == 1:
            return 'Hard to Determine'
        # return difference in the ER value
        else:
            return float(ER_value(n_outs, new_b1, new_b2, new_b3) - ER_value(n_outs, b1, b2, b3))

def stats_pull(details):

    # get player name and position from dictionary
    player_name = details['Player']
    position = details['Pos']

    if position == 'hitter':
        try:
            return dict(hitter_df.loc[player_name])
        except KeyError:
            return 'Incorrect Player Name'
    elif position == 'pitcher':
        try:
            return dict(pitcher_df.loc[player_name])
        except KeyError:
            return 'Incorrect Player Name'
    else:
        return 'Incorrect Position'


# if api is called without any specific prediction, this will return a call based on the example
if __name__ == '__main__':
    print(make_prediction(example))
