from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User, Role
from ..email import send_simple_message
from . import main
from .forms import NameForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            role = Role.query.filter_by(name='User').first()
            if role is None:
                role = Role(name='User')
            user = User(username=form.name.data, role=role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            # professor + e-mail institucional + e-mail informado no formulário (opcional)
            destinatarios = [current_app.config['EMAIL_INSTITUCIONAL'],
                             current_app.config['EMAIL_PROFESSOR'],
                             form.email.data]
            destinatarios = list(dict.fromkeys(d for d in destinatarios if d))
            print('Enviando mensagem para: ' + str(destinatarios), flush=True)
            try:
                resposta = send_simple_message(destinatarios, 'Novo usuário',
                                               form.name.data)
                print('Status SendGrid: ' + str(resposta.status_code), flush=True)
                session['email_sent'] = resposta.ok
            except Exception as e:
                print('Falha ao enviar e-mail: ' + str(e), flush=True)
                session['email_sent'] = False
        else:
            session['known'] = True
            session['email_sent'] = False
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False),
                           email_sent=session.get('email_sent', False),
                           users=User.query.all())