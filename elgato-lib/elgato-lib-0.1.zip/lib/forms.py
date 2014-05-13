# -*- coding: utf-8 -*-
#from flask_wtf import
#from __future__ import unicode_literals
#from flask.ext.wtf import Form  # @UnresolvedImport
from wtforms import Form, SubmitField, validators, PasswordField, BooleanField
from flask.ext.wtf import RecaptchaField
from wtforms.fields.html5 import EmailField
from wtforms.fields import TextField
from db.models import User

from flask_security.forms import LoginForm, ForgotPasswordForm, get_form_field_label, SendConfirmationForm, \
    ConfirmRegisterForm, ChangePasswordForm
from config import SECURITY_LABEL_REMEMBER_ME, SECURITY_LABEL_LOGIN

from config import EG_USE_RECAPTCHA

class LoginCustForm(LoginForm):
    email = EmailField(u"Login (email)",    [validators.Required(u"Molimo unesite vašu email adresu."), validators.Email(u"Molimo unesite vašu email adresu.")])
    password = PasswordField(u'Lozinka', [validators.Required(u"Molimo unesite lozinku.")])
    # def __init__(self, *args, **kwargs):
    #     LoginForm.__init__(self, *args, **kwargs)
    #     del self.remember
    remember = BooleanField(SECURITY_LABEL_REMEMBER_ME)
    submit = SubmitField(SECURITY_LABEL_LOGIN)

class ForgotPasswordCustForm(ForgotPasswordForm):
    if EG_USE_RECAPTCHA:
        recaptcha = RecaptchaField(label=u'Anti-robot kod', description=u'Unesite kod sa slike', validators=[validators.Required("Obavezno polje")])
    submit = SubmitField(get_form_field_label('recover_password'))
    pass

class SendConfirmationCustForm(SendConfirmationForm):
    if EG_USE_RECAPTCHA:
        recaptcha = RecaptchaField(label=u'Anti-robot kod', description=u'Unesite kod sa slike', validators=[validators.Required("Obavezno polje")])
    submit = SubmitField(get_form_field_label('send_confirmation'))

#from wtforms import FileField, File
class RegisterCustForm(ConfirmRegisterForm):
    firstname = TextField(label=u"Vaše ime",
                          validators=[validators.Required(u"Unesite Vaše ime"),
                                      validators.Length(max=30)],
                          description=u"Molimo unesite Vaše stvarno ime, jer ovaj podatak kasnije ne možete jednostavno promijeniti.")
    lastname = TextField(label=u"Vaše prezime",
                         validators=[validators.Required(u"Unesite Vaše prezime"),
                                     validators.Length(max=30)],
                         description=u"Molimo unesite Vaše stvarno prezime, jer ovaj podatak kasnije ne možete jednostavno promijeniti.")
    email = EmailField(label=u"Vaš email",
                       default=" ",
                       validators=[validators.Required(u"Unesite Vašu email adresu"),
                                   validators.Email(u"Unesite Vašu email adresu."),
                                   validators.Length(max=30)],
                       description=u"Ovaj email je ujedno i Vaše korisničko ime")
    city = TextField(label=u"Mjesto u kojem živite", validators=[validators.Required(),
                                                                 validators.Length(max=30)])
    zipcode = TextField(label=u"Poštanski broj mjesta", validators=[validators.Required(),
                                                                    validators.Length(min=5),
                                                                    validators.length(max=5)])
    password = PasswordField(label=u'Lozinka',
                             default=" ",
                             validators=[
                                         validators.Required(u"Unesite vašu lozinku"),
                                         validators.EqualTo('confirm', message=u'Niste ponovili istu lozinku'),
                                         validators.Length(max=30),
                                         validators.Length(min=6, message=u'Lozinka mora imati najmanje šest znakova.')])
    confirm = PasswordField(label=u'Ponovite lozinku', validators=[validators.Required("Obavezno polje")])

    if EG_USE_RECAPTCHA:
        recaptcha = RecaptchaField(label=u'Anti-robot kod', description=u'Unesite kod sa slike',
                                   validators=[validators.Required("Obavezno polje")])

    accept_tos = BooleanField(label=u'Prihvatam uslove korištenja')

    submit = SubmitField(label=u"Registrirajte se")

    def validate(self):
        if not super(ConfirmRegisterForm, self).validate():
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append(u"Ovaj email se već koristi")
            return False
        else:
            return True

#from wtforms import FileField, File
class ChangePasswordCustForm(ChangePasswordForm):
    pass

