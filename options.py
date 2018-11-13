from __future__ import division
from flask import Flask, request, redirect, url_for, render_template, jsonify, Markup

import os
import hashlib
import datetime, time, json, requests
from datetime import datetime, timedelta
from os import curdir, sep
from http.server import BaseHTTPRequestHandler, HTTPServer

# from flask_heroku import Heroku

from random import randint
import random

from db_setup import Subject, Portfolio, ChoiceProblem, Selection, db, app

import cgi
import collections, itertools

session = db.session

####
#####
######
####### __init__
######
#####
####

fixed_payment = 25 #fixed payment in cents
questions = 5 #number of questions per group
rounds = 2 #number of rounds.
groups = 1 #number of groups
delay = 7 #time till execution 

symbol = 'SPY'
av_api = "TDO6ET6NSGZF1MZ5"
API_URL = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol="+symbol+"&apikey=" + av_api


q = []

for i in range(questions):
    q.append(i) # +1 becuase sql counting starts a 1


permutations = list(itertools.permutations(q)) #all orderings of questions


####
#####
######
####### LOGIN PAGE
######
#####
####

@app.route('/')
@app.route('/login')
def Login():


        return render_template('login.html', text='Enter a subject number.', action='/user_manual', input=True, v=True)


####
#####
######
####### User information page
######
#####
####

### This route is the main landing page, it allows us to enter a username manually. It will accept
### any 6 or more charecter string as a user name (this is validated later, via the /user route)
### redirects to the /user with a formated URL

@app.route('/user_manual', methods=['POST', 'GET'])
def Manual():

    subject_id=request.form['subject_id']

    return redirect(url_for('newUser', workerId=subject_id), code=302)


### This is the route from M-TURK. takes the worker ID from the URL under workerID
### enters the subject if it does not exist in the data base.

@app.route('/user/', methods=['POST', 'GET'])
def newUser():

    subject_id = request.args.get('workerId')

    if len(subject_id) < 5:

        ### we resuse the login page as a prompt for payment, so v=true allows username entry.

        return render_template('login.html', text='Enter a valid subject number.', action='/user_manual', input=True, v=True)

    elif session.query(Subject).filter(Subject.idCode == subject_id).count() == 0:

        hashed_id = hashlib.sha1(subject_id.encode("UTF-8")).hexdigest()[:8]
        o = random.randint(0,len(permutations)-1) #choose order of questions for subject
        p = random.randint(0,rounds-1) #choose payment question
        g = random.randint(0,groups-1) #choose payment question

                
        subject = Subject(
            idCode= subject_id,
            hashed_id = hashed_id,
            time_start = datetime.now(),
            order = o,
            group = g,
            payment_question = p,
            total_payment = fixed_payment)    
        session.add(subject)
        session.commit()

        executeTime = (datetime.now() + timedelta(days=delay)).date()

        return render_template('instructions.html', subject_id = subject_id, rounds=str(rounds), fixed_payment=f'{round(fixed_payment/100, 2):.2f}', delay = delay, executeTime = executeTime, symbol=symbol)
        #return Quiz(subject_id) 
    else:
            return render_template('login.html', text='You have already Done this Study.', action='/user_manual', v=False)




### just routes the guy to the quiz. we could obviously totally get around this by formatting URLS
### and just making the redirect from the instructions directly. but why not. 

@app.route('/compquiz/<subject_id>', methods=['POST', 'GET'])
def Quiz(subject_id):

    j = session.query(Subject).filter(Subject.idCode == subject_id).one()


    if j.tryquiz:

        return render_template('login.html', text='You have already failed the quiz.', input=False, v=False)

    else:
        return render_template('quiz.html', subject_id = subject_id)

### now we need to make sure they passed the quiz. 

@app.route('/quizval', methods=['POST'])
def QuizVal():

    subject_id=str(request.form['subject_id'])
    j = session.query(Subject).filter(Subject.idCode == subject_id).one()


    if j.tryquiz:
        return render_template('login.html', text='You have already failed the quiz.', input=False, v=False)

    quiz_ans=[int(request.form['q1']),int(request.form['q2']),int(request.form['q3'])]
    correct = [0,1,0]
 
    print([(x+y)%2 for x, y in zip(quiz_ans, correct)])
    if [(x+y)%2 for x, y in zip(quiz_ans, correct)] == [0,0,0]:

        j.tryquiz = True
        j.passquiz = True
        session.add(j)
        session.commit()

        return WaitNext(subject_id,0)

    else:

        j.tryquiz = True
        j.passquiz = False
        session.add(j)
        session.commit()

        hashed_id = j.hashed_id

        text = Markup("""
        You failed the quiz.
        <br><br>
        You total payment is $"""+f'{round(j.payment/100, 2):.2f}'+""".
        <br><br>
        Please enter the following paycode on Amazon M-Turk: 
        <br><br><br>
        <h1>"""+str(hashed_id)+"""</h1>"""
         )

        return render_template('login.html', text=text, v=False)

### landing page.

@app.route('/waitnext/<subject_id>/<rnd>', methods=['POST'])
def WaitNext(subject_id,rnd):

    j = session.query(Subject).filter(Subject.idCode == subject_id).one()
    rnd = int(rnd)

    if rnd == 0:

        text = Markup("""
            <p style="text-align:left;">
            Congratulations! You passed the comprehension quiz and will now move on to the main part of the study.
            """)

        return render_template('login.html', text=text, action=url_for('ChoiceProblemApp', subject_id=subject_id, rnd=rnd), input=False, v=True)
    
    elif rnd < rounds:

        p_choice = request.form['cp']

        sel_num = session.query(Selection).filter(Selection.subject == j.id, Selection.rnd == rnd -1 ).count()

        if (sel_num > 1):
            return render_template('login.html', text='You cannot change your anwsers.', input=False, v=False)
        else:
            sel = session.query(Selection).filter(Selection.subject == j.id, Selection.rnd == rnd -1 ).one()


            sel.choice = p_choice,
            sel.time_end = datetime.now()

            session.add(sel)
            session.commit()

            return ChoiceProblemApp(subject_id,rnd)

    else:

        p_choice = request.form['cp']

        sel = session.query(Selection).filter(Selection.subject == j.id, Selection.rnd == rnd -1 ).one()

        sel.choice = p_choice,
        sel.time_end = datetime.now()
        
        session.add(sel)
        session.commit()


        return render_template('survey.html', subject_id=subject_id,)


####
#####
######
####### Create Sets Page
######
#####
####

### this generates the page with the cards on it.

@app.route('/choiceproblem/<subject_id>/<rnd>', methods=['POST', 'GET'])
def ChoiceProblemApp(subject_id,rnd):

    rnd = int(rnd)
    next_rnd = rnd + 1

    j = session.query(Subject).filter(Subject.idCode == subject_id).one()


    #make sure that the user has not already seen this page, otherwise redirect
    sel_num = session.query(Selection).filter(Selection.subject == j.id, Selection.rnd == rnd).count()
    ans = False
    if (sel_num == 1):
        sel = session.query(Selection).filter(Selection.subject == j.id, Selection.rnd == rnd).one()
        ans = sel.choice
    
    if (ans):
        return render_template('login.html', text='You cannot change your anwsers.', input=False, v=False)
    else:

        o = j.order
        perm = permutations[o] #this is the order of questions for suject
        qindex = perm[rnd] # current qestion
    
        q = session.query(ChoiceProblem).filter(ChoiceProblem.group == j.group).all()[qindex]
        CP_type = q.CP_type ## current choice problem as string.
        CPid = q.id
    
    
    
        port_arr = []
        for i in range(len(CP_type)):
            if (CP_type[i] == "1"):
                p = session.query(Portfolio).filter(Portfolio.group == j.group, Portfolio.p_type==i).one()
                port_arr.append([f'{round(p.cash/100, 2):.2f}'+":"+f'{round(p.long_share/100, 2):.2f}', p.id])
    
        ## permute the order of qustions
        random.shuffle(port_arr)
    
    
        response = requests.get(API_URL)
        data = response.json()
        current_price = float(data['Global Quote']['08. previous close'])

        if (sel_num == 0):
            #create new selection entry, no selection is made, update after submision. 
            selection = Selection(
                choice_problem = CPid,
                begining_price = current_price,
                rnd = rnd, 
                time_start = datetime.now(),
                subject = j.id)    
            session.add(selection)
            session.commit()

        return render_template('choiceproblem.html', subject_id = subject_id, current_price=f'{round(current_price, 2):.2f}', symbol=symbol, port_arr=port_arr, action=url_for('WaitNext', subject_id=subject_id, rnd=next_rnd),rnd=rnd)


@app.route('/end', methods=['POST'])
def End():

    subject_id=str(request.form['subject_id'])
    j = session.query(Subject).filter(Subject.idCode == subject_id).one()
    print(j.payment_question)
    sel = session.query(Selection).filter(Selection.subject == j.id, Selection.rnd == j.payment_question).one()
    p = session.query(Portfolio).filter(Portfolio.id == sel.choice).one()
    p_data = f'{round(p.cash/100, 2):.2f}'+":"+f'{round(p.long_share/100, 2):.2f}'

    j.age = request.form['age']
    j.gender = request.form['gender']
    j.degree = request.form['degree']

    session.add(j)
    session.commit()

    text = Markup("""
            Thank you. 
            <br>
            The selected question was question """+str(j.payment_question + 1)+""". You chose the 
            portfolio <br><br>
            <span class=port data="""+p_data+"""></span>
            <br><br>
            The value of this portfolio will be calculated on """ + str((datetime.now() + timedelta(days=delay)).date())+"""
            <br><br>
            Please enter the following paycode on Amazon M-Turk: 
            <br><br><br>
            <h1>"""+str(j.hashed_id)+"""</h1>"""
             )



    return render_template('login.html', text=text, v=False)

    


    




if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')

 