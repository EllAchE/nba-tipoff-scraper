from src.database.data_update import customDataUpdate

# customDataUpdate()
from src.live_data.display_bets import getAllOddsAndDisplayByEv
from src.live_data.live_odds_retrieval import betfairOdds, getDailyOdds
#
# getDailyOdds('BOS', 'SAC', '-105')


getAllOddsAndDisplayByEv(mgm=True)