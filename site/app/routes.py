from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
#from flask_sqlalchemy import SQLAlchemy
from app import app, models, db
from app.forms import LoginForm, RegistrationForm, SpellCheckForm, HistoryAdminForm, LoginHistUserForm
from app.models import User, TestLog, SecLog
from app.utils import perform_spellcheck



debug = True

@app.route('/')
@app.route('/index')
@login_required #force a login to view this page
def index():
    return redirect(url_for('spell_check'))

@app.route('/login', methods=['GET','POST'])
def login():
    if(current_user.is_authenticated):
        return redirect(url_for('index'))
    form = LoginForm()
    if(form.is_submitted()):
        if(form.validate()):
            uname = form.username.data
            print("User: "+uname)
            pword = form.password.data
            mfaid = form.mfacode.data
            #print(uname+":"+pword+":"+mfaid)
            #grab the user field, and perform a query by it, and grab the first result
            user = User.query.filter_by(username=uname).first()
            #if we get no user (username mismatch) or password is wrong, say invalid
            if(user == None or not user.checkpw(pword)):
                return render_template('login_results.html', title='Login Failed', form=form, results="Login failure: Incorrect username or password")
            if(not user.checkmfaid(mfaid)):
                return render_template('login_results.html', title='Login Failed', form=form, results="Login failure: Two-factor auth failure")
            login_user(user)
            models.write_login(user)
            return render_template('login_results.html', title='Login Success', form=form, results="Login success")
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if(current_user.is_authenticated):
        return redirect(url_for('index'))
    form = RegistrationForm()
    if(form.is_submitted()):
        if(form.validate()):
            #test user existance
            uname = form.username.data
            pword = form.password.data
            mfaid = form.mfaid.data
            #print(uname+":"+pword+":"+mfaid)
            #note, this doesn't actually do anything, since the RegForm already has a validator on name
            user = User.query.filter_by(username=uname).first()
            if(user != None):
                return render_template('register_results.html', title='Register Failed', form=form, results="Registration failure: username in use")
            user = User(username=uname, mfaid=mfaid)
            user.setpw(pword)
            db.session.add(user)
            db.session.commit()
            return render_template('register_results.html', title='Register Successful', form=form, results="Registration success")
        else:
            return render_template('register_results.html', title='Register Failed', form=form, results="Registration failure: invalid fields")
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
@login_required #force a login to view this page
def logout():
    models.write_logout(current_user)
    logout_user()
    return redirect(url_for('index'))


@app.route('/spell_check', methods=['GET', 'POST'])
@login_required #force a login to view this page
def spell_check():
    form = SpellCheckForm()
    if(form.validate_on_submit()):
        textout = form.textin.data
        misspelled = []
        perform_spellcheck(form.textin.data, misspelled)
        models.write_test(current_user, textout, misspelled)
        return render_template('spellcheckout.html', title='Spell Check Results', form=form, textout=textout, misspelled=misspelled)
    return render_template('spellcheckin.html', title='Enter Text to Spell Check', form=form)

@app.route('/history', methods=['GET', 'POST'])
@login_required #force a login to view this page
def history():
    #process the admin
    if(current_user.level==0):
        form = HistoryAdminForm()
        if(form.is_submitted()):
            if(form.validate()):
                uname = form.username.data
                #look up the user
                u = User.query.filter_by(username=uname).first()
                if(u==None):
                    return render_template('history_admin_userquery.html', title='ADMIN: Select a user to query the history for', form=form)
                #render the user history list
                return render_template('history.html', title='User Test History', user=u)
        else:
            #render the user query form
            return render_template('history_admin_userquery.html', title='ADMIN: Select a user to query the history for', form=form)
    else:
        return render_template('history.html', title='User Test History', user=current_user)


@app.route('/history/query<int:test_id>', methods=['GET', 'POST'])
@login_required #force a login to view this page
def history_query(test_id):
    tst = TestLog.query.filter_by(id=test_id).first()
    if(tst!=None):
        if(current_user.id==tst.user_id or current_user.level==0):
            return render_template('historyquery.html', title='Test '+str(tst.id), tst=tst)
    return "<html><body>No info available</body></html>"


@app.route('/login_history', methods=['GET', 'POST'])
@login_required #force a login to view this page
def login_history():
    #process the admin
    if(current_user.level==0):
        form = LoginHistUserForm()
        if(form.is_submitted()):
            if(form.validate()):
                uname = form.username.data
                #look up the user
                u = User.query.filter_by(username=uname).first()
                if(u==None):
                    return render_template('loginhist.html', title='ADMIN: Select a user to query the history for', form=form)
                #render the login history list
                return render_template('loginhist_results.html', title='User Login History', user=u)
        else:
            #render the user query form
            return render_template('loginhist.html', title='ADMIN: Select a user to query the history for', form=form)
    else:
        abort(404)

