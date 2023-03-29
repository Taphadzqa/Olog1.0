from blank.core.models import User, Company
from sqlalchemy.exc import SQLAlchemyError
from flask import url_for, flash
from blank import db, bcrypt
import smtplib
import string
import random

# Email credentials
smtp = 'smtp.orangelogistics.co.za'
username = 'tafa@orangelogistics.co.za'
password = 'bonfire6POLARITY@defeat'
sender = 'noreply@olog.co.za'


#RESET PASSWORD
def sendResetEmail(user):
    server = smtplib.SMTP_SSL(smtp, 465)
    token = user.get_reset_token()
    msg = 'Subject: OLOG - Password reset \nDo not reply to this sender\n\nTo reset your password, visit the link below:\n' + url_for('user.reset_token', token=token, _external=True) + '\n\nIf you did not make this request, please ignore this email and no changes will be made to your account'
    server.login(username, password)
    server.sendmail(sender, user.email, msg)
    server.quit()


# SEND AN EMAIL
def sendEmail(email, msg):
    server = smtplib.SMTP_SSL(smtp, 465)
    server.login(username, password)
    server.sendmail(sender, email, msg)
    server.quit()


# Get list of active companies
def getCompanies():
    companies = [(co.id, co.name) for co in Company.query.filter(Company.status!='No').order_by(Company.name).all()]
    return companies


#Generate random string
def generateString(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Add user to the database
def addUser(name, email, role, status, company):
    password = generateString()
    hashed_password = bcrypt.generate_password_hash(password) # Generate and harsh user's password
    msg = 'Subject: OLOG\nDo not reply to this sender\n\nYour password is ' + password # Email message
    user = User(name=name, email=email, password=hashed_password, role=role, status=status, company_id=int(company)) # Create a user object
    db.session.add(user)
    try:
        db.session.commit()
        sendEmail(email, msg)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        flash('We experienced an internal error. Please try again.\n\n\n' + error, 'warning')
        return False
    else:
        return True
