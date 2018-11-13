    

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
import itertools

import db_setup

from db_setup import Subject, Portfolio, ChoiceProblem, Selection, db, app
 

db.drop_all()
db.create_all()

session = db.session


## create portfolios list of lists of portfolios (inner list groups by GROUP)
## that is, each inner list should contain 6 portfolios, one of each type:

#0: cash_init 
#1: long_init 
#2: cash_attr 
#3: long_attr 
#4: cash_comp 
#5: long_comp 


portfolio_list = [
[ #group 0
{'cash': 500, 'long_share': 35, 'time': 7, 'p_type': 0}, #cash_init 
{'cash': 300, 'long_share': 75, 'time': 7, 'p_type': 1}, #long_init
{'cash': 400, 'long_share': 30, 'time': 7, 'p_type': 2}, #cash_attr 
{'cash': 200, 'long_share': 70, 'time': 7, 'p_type': 3}, #long_attr
{'cash': 600, 'long_share': 25, 'time': 7, 'p_type': 4}, #cash_comp 
{'cash': 200, 'long_share': 90, 'time': 7, 'p_type': 5} #long_comp
]
]

#we do not care about every collection of portfolios, so lets choose the ones we care about.

#i just did single decoys for now, we can add more later.

CP_type_list = [
'110000', #no decoys
'111000', #cash_attr decoy only
'110100', #long_attr decoy only
'110010', #cash_comp decoy only
'110001', #long_comp decoy only
]

for i in range(len(portfolio_list)):

    for p in portfolio_list[i]:

        new_portfolio = Portfolio(
            cash = p['cash'],
            long_share = p['long_share'],
            time = p['time'],
            group = i,
            p_type = p['p_type'])
        session.add(new_portfolio)

    for t in CP_type_list:
        new_CP = ChoiceProblem(
            group = i,
            CP_type = t)
        session.add(new_CP)
        
session.commit()


print("db initialized!")   


