    

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
import itertools

import db_setup

from db_setup import Subject, Portfolio, ChoiceProblem, Selection, db, app
 

session = db.session

subs = session.query(Subject).all()

for j in subs:
    print(j.idCode, j.tryquiz, j.passquiz)


sels = session.query(Selection).all()

for s in sels:
    print(s.choice_problem, s.choice, s.rnd)
