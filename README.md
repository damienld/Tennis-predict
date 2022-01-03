# Tennis-predict
Predict the outcome of ATP/WTA matches based on advanced features

## 1 - Collect Data from OnCourt SQL Db
- The data is collected from the MS Access Db provided with OnCourt software throught the model object developped in C# and extracted as CSV. (**ToDo**: directly read/load SQL from this project without the C# transition)
- The CSV are loaded year by year and contain the list of all matches with match/player/tournament info:
    - Date: Date fo the match
    - TrnId: If of tournament
    - Trn: Name of tournament
    - TrnRk: Tournament Category (1= ITF 25k+ and CHAL / 2 ATP 250&500 / 3 Masters and Masters 1000 / 4 Slams / 5 Davis Cup / 6 Exhib + Juniors + Hopman + Mubadala ..)
    - TrnSite
    - TrnSpeed: Speed of tournament as calculated by another model
    - TrnSpeedNb: # of matches for TrnSpeed calc
    - CourtId: Surface (1= Hard, 2= Clay, 3=Indoor, 4=Carpet, 5=Grass)
    - RoundId: Round of the tournament (1-3= Qual, 4= R1 ..., 12= F)
    - Round: Round name
    - P1Id: Id player 1
    - P1: Name player 1
    - P2Id: Id player 2
    - P2: Name player 2
    - Result
    - IndexP: Index of winner (0=P1, 1=P2)
    - Player: winning player name
    - Rk1: ATP Ranking of P1
    - Rk2: ATP Ranking of P2
    - Odds1: pinnacle odds for P1
    - Odds2: pinnacle odds for P2
    - IsCompleted: True/False if match was completed or not
    - SetsP1: # sets won by P1
    - SetsP2: # sets won by P2
    - GamesP1: # sets won by P1
    - GamesP2: # sets won by P2
    - Duration
    - Age1
    - Age2
- The global dataframe is a concatenation of all the yearly csv with all matches
- The CSV actually contains 2 rows per match, one for each player, we will only keep one row per match

## 2 - Build ELO ratings for each match
- Implement the ELO basic rating (elorating.py)
    - **PlayerElo** object will represent a player with his historical Elo rating after each match, it contains 2 dictionnaries:
        - eloratings: {date*: new ELO rating after this date}
        - elomatches: {date*: number of matches compiled for the ELO rating}
        - The date is defined as a string "YYYYMMDDn" where n is the index of the match for that day (as a player can play several matches in a day sometimes). This format easily allowed to sort/access the ratings.   
        - The first date is set to -1
    - **initial rating**: we had 2 choices here (2nd one was selected after trying both)
        - turn the official current ATP ranking of the player into an ELO estimation for this rank (a rough mapping was done)
        - start everyone at the same level and ignore the first year as it will be calibrating the ELO of each player
- Adapt it to Tennis
- Export it year by year to csv (to be used in another project)
- Filter tournaments that should be excluded (5 = DC / exclude CAT 6 = Exhib but keep "XXX (juniors)" / "Hopman Cup" / "Mubadala 
- manage players long period out

ToDo:
- manage new entrants
- Test the different settings to find the most efficient one (KCoeffOpp, startingElo..)
- 
## 3 - Add extra features (ToDo)
- Recent ELO
- Elo depending on score gap
- ELO Rating by Surface
- Peak ELO with date
- Cumulated Fatigue
- H2H
- ROI vs style of player
- Trn history
..

## 4 - Preprocessing
- Standardization
- Outliers

## 5 - Compare Models
- Split data train/validation/test
- Fit
- Cross Validation KFold
- Hyperparameters tuning
- ML
- DL
- Define a metric for evaluation (F1-score, raw ROI, ROi with Kelly staking..)

## 6 - Test

## 7 - Deploy
