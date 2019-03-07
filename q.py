from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
#import itertools
import pandas as pd


import db_setup

from db_setup import Subject, Portfolio, ChoiceProblem, Selection, db, app
 

session = db.session



subs_df = pd.read_sql(session.query(Subject).filter(Subject.passquiz==True).statement,session.bind) 
sels_df = pd.read_sql(session.query(Selection).statement,session.bind) 

CP_type_list = [
['110000', 'init'],
['111000', 'cash_attr'],
['110100', 'long_attr'],
['110010', 'cash_comp'],
['110001', 'long_comp'],
]

#add a column with the ID
for t in CP_type_list:
    t.append(session.query(ChoiceProblem).filter(ChoiceProblem.CP_type == t[0]).one().id)


#create new cols for each
for t in CP_type_list[1:]:
    
    subs_df["sw_"+t[1]] = 'cons'
    
for sub in session.query(Subject).filter(Subject.passquiz==True).all():
    for t in CP_type_list[1:]:
        
        sel = session.query(Selection).filter(Selection.choice_problem == t[2]).filter(Selection.subject == sub.id).one()
        init_sel = session.query(Selection).filter(Selection.choice_problem == 1).filter(Selection.subject == sub.id).one()
        
        if sel.choice != init_sel.choice:
            subs_df["sw_"+t[1]] = 'switch'