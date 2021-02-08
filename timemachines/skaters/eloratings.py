from timemachines.skaters.allskaters import SKATERS, skater_from_name  # Only those with no hyper-params
from timemachines.skaters.evaluation import evaluate_mean_squared_error, evaluator_from_name
import numpy as np
from pprint import pprint
from timemachines.data.live import random_regular_data
from timemachines.common.eloratings import elo_update  # TODO: Use ratings package instead


SKATER_ELO_F = 1000  # The scale factor for ratings. In chess this is set to 400.
                     # If the matchup is considered more fluky than a single game of chess, a higher value might make sense.


def skater_elo_update(elo: dict, k, evaluator=None, n_burn=400, tol=0.01, initial_elo=1600, data_source =None):
    """ Create or update elo ratings by performing a random matchup on univariate live data

          elo - Dictionary containing the 'state' (i.e. elo ratings and game counts)
          k   - Number of steps to look ahead
          tol - Error ratio that results in a tie being declared
          data_provider - A function returning y, t

        Speed is not taken into account
    """
    if data_source is None:
        data_source = random_regular_data

    if not elo:
        # Initialize game counts and Elo ratings
        elo['name'] = [f.__name__ for f in SKATERS]
        elo['count'] = [0 for _ in SKATERS]
        elo['rating'] = [initial_elo for _ in SKATERS]
        elo['traceback'] = ['not yet run' for _ in SKATERS]
        elo['active'] = [True for _ in SKATERS]

    else:
        # Check for newcomers
        new_names = [f.__name__ for f in SKATERS if f.__name__ not in elo['name']]
        for new_name in new_names:
            elo['name'].append(new_name)
            elo['count'].append(0)
            elo['rating'].append(initial_elo)
            elo['traceback'].append('not yet run')
            elo['active'].append(True)

    if evaluator is None:
        if elo.get('evaluator'):
             evaluator = evaluator_from_name(elo.get('evaluator'))
        else:
            evaluator = evaluate_mean_squared_error
        elo['evaluator'] = evaluator.__name__

    n_skaters = len(elo['name'])
    i1, i2 = np.random.choice(list(range(n_skaters)), size=2, replace=False)
    skater1, skater2 = elo['name'][i1], elo['name'][i2]
    fs = list()
    for i,sn in zip([i1,i2],[skater1,skater2]):
        try:
            f = skater_from_name(sn)
            elo['active'][i] = True
            fs.append(f)
        except Exception as e:
            elo['active'][i]=False

    if len(fs)==2:
        # a pitched paddle battle in a bottle
        print(fs[0].__name__ +' vs. '+fs[1].__name__)
        y, t = random_regular_data(n_obs=n_burn+50)
        scores = list()
        for i, f in zip([i1,i2],fs):
            import traceback
            try:
                score = evaluator(f=f, y=y, k=k, a=None, t=t, e=None, n_burn=n_burn)
                elo['traceback'][i] = 'passing'
                scores.append(score)
            except Exception as e:
                elo['traceback'][i] = traceback.format_exc()

        if len(scores)==2:
            small = tol * (abs(scores[0]) + abs(scores[1]))  # Ties
            points = 1 if scores[0] < scores[1] - small else 0 if scores[1] < scores[0] - small else 0.5
            elo1, elo2 = elo['rating'][i1], elo['rating'][i2]
            min_games = min(elo['count'][i1],elo['count'][i2])
            K = 16 if min_games > 25 else 25  # The Elo update scaling parameter
            elo['rating'][i1], elo['rating'][i2] = elo_update(elo1, elo2, points,k=K,f=SKATER_ELO_F)
            elo['count'][i1] += 1
            elo['count'][i2] += 1

    return elo







