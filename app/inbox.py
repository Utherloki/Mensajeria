from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_file
)

from app.auth import login_required
from app.db import get_db

bp = Blueprint('inbox', __name__, url_prefix='/inbox')

@bp.route("/getDB")
@login_required
def getDB():
    return send_file(current_app.config['DATABASE'], as_attachment=True)


@bp.route('/show')
@login_required
def show():
    
    db = get_db()   ## Codigo(OK)
    messages = db.execute(
        'SELECT message.subject, message.body, message.created, user.username FROM message INNER JOIN user ON message.from_id = user.id WHERE message.to_id= ? ORDER BY created DESC', (str(g.user['id']))      ## Codigo(VERIFICAR QUERY ??)
    ).fetchall()
    # print(str(g.user['id']))
    # print ('user')

    return render_template('inbox/show.html', messages=messages)    ## Codigo(VERIFICAR QUERY ??)
 

@bp.route('/send', methods=('GET', 'POST'))
@login_required
def send():
    if request.method == 'POST':
        from_id = g.user['id']                  ## Codigo(VERIFICAR  ??)
        to_username = request.form['to']        ## Codigo(VERIFICAR  ??)
        subject = request.form['subject']       ## Codigo(VERIFICAR  ??)
        body = request.form['body']             ## Codigo(VERIFICAR  ??)
        
        db = get_db()       ## Codigo(OK)
       
        if not to_username:
            flash('To field is required')
            return render_template('inbox/send.html')   ## Codigo(OK) 
        
        if not subject:     ## Codigo(OK)
            flash('Subject field is required')
            return render_template('inbox/send.html')
        
        if not body:        ## Codigo(OK)
            flash('Body field is required')
            return render_template('inbox/send.html')       ## Codigo(OK) 
        
        error = None    
        userto = None 
        
        userto = db.execute(
            # 'SELECT id FROM user WHERE email = ?', (to_username,)
            'SELECT * FROM user WHERE username = ?', (to_username,)      ## Codigo(OK_JD)
            
        ).fetchone()
        print('userto')
        if userto is None:
            error = 'Recipient does not exist'
     
        if error is not None:
            flash(error)
        else:
            db = get_db()       ## Codigo(OK)
            db.execute(
                'INSERT INTO message (from_id , to_id, subject, body) VALUES (?,?,?,?)',    ## Codigo(VERIFICAR QUERY ??)
                (g.user['id'], userto['id'], subject, body)
            )
            db.commit()

            return redirect(url_for('inbox.show'))

    return render_template('inbox/send.html')