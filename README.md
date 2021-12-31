# Tennis-predict
Predict the outcome of ATP/WTA matches based on advanced features

## 1 - Collect Data from OnCourt SQL Db
- The data is collected from the model object developped in C# and extracted as CSV.
- The CSV are loaded year by year

## 2 - Build ELO ratings for each match
- Implement the ELO basic rating
- Adapt it to Tennis
- Export it year by year to csv (to be used in another project)
- Filter tournaments that should be excluded (5 = DC / exclude CAT 6 = Exhib but keep "XXX (juniors)" / "Hopman Cup" / "Mubadala 

ToDo:
- manage players long period out
- manage new entrants
- Test the different settings to find the most efficient one (KCoeffOpp, startingElo..)
- 
## 3 - Add extra features (ToDo)
- Recent ELO
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
