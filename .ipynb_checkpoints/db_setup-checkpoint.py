

# from flask_sqlalchemy import SQLAlchemy

from flask import Flask, request, redirect, url_for, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

from flask_heroku import Heroku

app = Flask(__name__)

import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import create_engine

## long pg uri is heroku hosted, short is local pg
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://qkjkmzsxebomeb:e30bc41f94fd7d18da8f8d72ae0c3849847f74f06aef507debbf0b936077df53@ec2-54-235-193-0.compute-1.amazonaws.com:5432/d1kaup4k5s62fe'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/Options'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#heroku = Heroku(app)
db = SQLAlchemy(app)



## Subject Tabel. Each entry is a user. Generated at logon

class Subject(db.Model):
    __tablename__ = 'subject'
    id = Column(Integer, primary_key=True)
    idCode = Column(String(100))
    hashed_id = Column(String(100)) #used for M-Turk validation
    time_start = Column(DateTime) #when did she start the question
    tryquiz = Column(Boolean, default=False)
    passquiz = Column(Boolean, default=False)
    current_rnd = Column(Integer, default=0) #gets updated as subject progresses. back navigation restrictions / generate questions via order
    order = Column(Integer) # integer describing the order, from list of permutations
    payment_question = Column(Integer, default=0) #which question do we pay (rnd)
    total_payment = Column(Integer, default=0) #total payment, cents
    group = Column(Integer, default=0) #which group of portfolios make up the choice problems
    age = Column(Integer) #survey questions
    gender = Column(Integer)
    location = Column(Integer)

## portfolios: a portfolio is a choice element, it is of the form 
##(fixed payment, share of S&P500, time till execute )

### a GROUP is a set of 6 portfolios; one of each of the following types:

#0: #0: cash_init ::: inital port, good in cash dim
#1: #1: long_init ::: inital port, good in long dim
#2: #2: cash_attr ::: attration effect, dominated by cash (makes cash_init target)
#3: #3: long_attr ::: attration effect, dominated by long (makes long_init target)
#4: #4: cash_comp ::: comp effect, makes cash_init target
#5: #5: long_comp ::: comp effect, makes long_init target

### a CP_TYPE is a binary encoding of a choice problem (as a string)

## i.e., 110000 is the CP with p_types 0 and 1 and no others.


##generated by initdb.py

class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = Column(Integer, primary_key=True)
    cash = Column(Integer) #cash payment
    long_share = Column(Integer) #share in s&p, dominated in percent (0-100)
    time = Column(Integer) #time of option execution, payment, in days from start time
    group = Column(Integer, default=0) #a group is a collection of portfolios that one subject sees.
    p_type = Column(Integer) #a portfolio type is 1 of the 6 above types. 

# choice problems --- collections of portfolios
## each can be described by 6 (possibly empty) portfolios

class ChoiceProblem(db.Model):
    __tablename__ = 'choice_problem'

    id = Column(Integer, primary_key=True)
    group = Column(Integer, default=0) #a group is a collection of portfolios that one subject sees.
    CP_type = Column(String, default='110000') #a CP_type is a binary encoding of which p_types are in the CP


#selections -- what did subjects choose

class Selection(db.Model):
    __tablename__ = 'slection'
    id = Column(Integer, primary_key=True)
    choice_problem = Column(Integer, ForeignKey("choice_problem.id")) #which choice problem
    choice = Column(Integer, ForeignKey("portfolio.id")) # the anwser
    time_start = Column(DateTime) #when did she start the question
    time_end = Column(DateTime) #when did she end the question
    beginning_price = Column(Integer) #sp500 price at time start --- demonomiated in cents
    ending_price = Column(Integer) #sp500 price at exicute (post exp)
    chart_time = Column(Integer) #how long was the chart open, ms
    click_hist = Column(String) #prior clicks: array with [portfolio id, JS time], in JSON string format
    rnd = Column(Integer) #when did the subject do this?
    subject = Column(Integer, ForeignKey("subject.id")) #who was is?