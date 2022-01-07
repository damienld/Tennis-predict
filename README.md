# Tennis-predict
Predict the outcome of ATP/WTA matches based on advanced features

## 1 - Collect Data from OnCourt SQL Db
- The data is collected from the MS Access Db provided with OnCourt software throught the model object developped in C# and extracted as CSV. (**ToDo**: directly read/load SQL from this project without the C# transition)
- The CSV are loaded year by year and contain the list of all matches with match/player/tournament info (the full detail is listed at the end of this document):
    - Date: Date fo the match
    - CourtId: Surface (1= Hard, 2= Clay, 3=Indoor, 4=Carpet, 5=Grass)
    - P1: Name player 1
    - P2: Name player 2
    - Result
    - IndexP: Index of winner (0=P1, 1=P2)
    - Rk1: ATP Ranking of P1
    - Rk2: ATP Ranking of P2
    - Odds1: pinnacle odds for P1
    - Odds2: pinnacle odds for P2
    - IsCompleted: True/False if match was completed or not
    - SetsP1: # sets won by P1
    - SetsP2: # sets won by P2
    ..
- The global dataframe is a concatenation of all the yearly csv with all matches
- The CSV actually contains 2 rows per match, one for each player, we will only keep one row per match
- Some tournaments are not taken into account (exclude TrnRk=6 (Exhib) but keep "XXX (juniors)" / "Hopman Cup" / "Mubadala) 


## 2 - Build ELO ratings for each match
**ELO rating** (Wikpedia):
The **difference in the ratings between two players serves as a predictor** of the outcome of a match. Two players with equal ratings who play against each other are expected to score an equal number of wins. A player whose rating is 100 points greater than their opponent's is expected to score 64%; if the difference is 200 points, then the expected score for the stronger player is 76%.

A player's Elo rating is represented by a number which may change depending on the outcome of rated games played. 
After every game, the winning player takes points from the losing one. The difference between the ratings of the winner and loser determines the total number of points gained or lost after a game. If the higher-rated player wins, then only a few rating points will be taken from the lower-rated player. However, if the lower-rated player scores an upset win, many rating points will be transferred. The lower-rated player will also gain a few points from the higher rated player in the event of a draw. This means that this rating system is self-correcting. Players whose ratings are too low or too high should, in the long run, do better or worse correspondingly than the rating system predicts and thus gain or lose rating points until the ratings reflect their true playing strength.

**K-factor**
Elo’s K-factor **determines how quickly the rating reacts to new game results**. It should be set so as to efficiently account for new data but not overreact to it. (In a more technical sense, the goal is to minimize autocorrelation.) If K is set too high, the ratings will jump around too much; if it’s set too low, Elo will take too long to recognize important changes in player quality.

- Implement the ELO basic rating (elorating.py) and some useful function to use it
    - **PlayerElo** object will represent a player with his historical Elo rating after each match, it contains 2 dictionnaries:
        - eloratings: {date*: new ELO rating after this date}
        - elomatches: {date*: number of matches compiled for the ELO rating}
        - The date is defined as a string "YYYYMMDDn" where n is the index of the match for that day (as a player can play several matches in a day sometimes). This format easily allowed to sort/access the ratings.   
        - The first date is set to -1
    - **initial rating**: we had 2 choices here (2nd one was selected after trying both)
        - turn the official current ATP ranking of the player into an ELO estimation for this rank (a rough mapping was done)
        - start everyone at the same level and ignore the first year as it will be calibrating the ELO of each player
- Adapting it to Tennis
    - Determining the best formula for K-factor:  
        - coeffKplayer = aCoeffK * 250 / ((nbmatches + 5) ** 0.4) (as per https://fivethirtyeight.com/features/serena-williams-and-the-difference-between-all-time-great-and-greatest-of-all-time/)
        - also it takes into account the round and tournament importance
        - additionnally if the ELO of the opponent is not really defined yet (less than 50 matches) K factor is largely decreased (as the opp's ELO rating can't be trusted)     
    - Management of players long periods out
        - 55 days out => Elo-100. 250 => Elo-150 (as per http://www.tennisabstract.com/blog/2018/05/15/handling-injuries-and-absences-with-tennis-elo/ )
        - but don't count tennis offseason (or covid suspension) when Tour is actually off (as it's not due to an injury/decision)
- Elo ratings history by players (JSON) must be Exportable year by year to csv (to be used in another project)


## 3 - First model - ELO1
The first model is done by just using the **ELO rating** defined above.
It is applied on ATP date (TrnRk>=2 from 2014 onwards)
We evaluate the difference between our prediction and the actual result:
- **Brier score for Elo 0.2055**
- Brier score for Odds 0.1878 (caclulated by using bookmaker odds)

We also calculate the ROI if we were betting every time our probability was quite different from the offered odds
- Applying Kelly criterion: 15*( (odds - 1) * myproba - (1 - myproba)) / (odds - 1) which gives for example 1 unit for 50% at 2.16 (2u for 40% at 3.24 ..) 
- **ROI model ELO1 = -5.9%**

Eventually, we compare the **accuracy of the following methods** to predict the **match winner**:
- best ATP ranking
- best ELO rating
- best odds

![](https://github.com/damienld/Tennis-predict/blob/main/img/readme/accuracy_by_methods_1.png)

## 4 - Add extra features (ToDo)
- ELO Rating by Surface (Clay and NonClay)
- Recent ELO
- Peak ELO with date
- update not just the Elo rating when managing long periods out BUT also the K-Factor as there is more doubt about that value
- Test the different settings to find the most efficient one (KCoeffOpp, startingElo, KFactor when player out..)
- Elo depending on score gap
- Cumulated Fatigue
- H2H
- ROI vs style of player
- Trn history
..
### 4.1 Adding Elo Court and Recent Elo
When looking at court(surface) by court analysis we will just divide them between clay and non clay (hard, indoor, grass, carpet) because there is not enough matches on grass for example to make a proper elo rating. The exact surface will be take into account later using another feature.
- Elo Court is an elo rating where we just take into account the matches played for all players on a specific surface (either clay or non clay)
- Recent Elo (9 months) is made of:
   - the intial rating of the player: his rating at the time of the first match (mixed rating between overall elo rating and court elo rating)
   - the number of matches played for ELO is set to 0 and incremented for each set taken into account
   - the Elo rating for last 9 months on court: applied set by set using the mixed rating(avg of overall rating and court rating) of the opponent

![](https://github.com/damienld/Tennis-predict/blob/main/img/readme/accuracy_by_methods_2.png)

## 5 - Preprocessing
- Standardization
- Outliers

## 6 - Comparing Models
- Split data train/validation/test
- Fit
- Cross Validation KFold
- Hyperparameters tuning
- ML
- DL
- Define a metric for evaluation (F1-score, raw ROI, ROi with Kelly staking..)

## 7 - Test

## 8 - Deploy


The loaded CSV contain the following:
    
    - Date: Date of the match
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
