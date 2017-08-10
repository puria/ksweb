
from formencode.validators import FieldsMatch
from resetpassword.lib.validators import RegisteredUserValidator
from tw2.core import Validator
from tw2.forms import FileField

from tw2.forms import TableForm, HiddenField, PasswordField, SubmitButton, TextField
from tg.i18n import lazy_ugettext as l_

import tw2.forms as twf
from tg import lurl


class ResetPasswordForm(twf.Form):
    class child(twf.TableLayout):
        inline_engine_name = 'kajiki'
        template = '''

                    <div  style="padding-top:20px">

                            <div class="col-md-12 ks-section-name">
                                Recover password
                                <hr/>
                            </div>
                            <div class="form-group col-md-4">

                                ${w.children.email_address.display()}
                             <span class="help-block" py:content="w.children.email_address.error_msg"/>
                            </div>
                     </div>
                '''
        email_address = TextField(label=l_('Email address'), validator=RegisteredUserValidator(required=True), css_class="form-control",placeholder=l_('Email address'))

    submit = SubmitButton(css_class="btn btn-primary", value=l_("Send"))

    action = lurl('/reset_request')


class NewPasswordForm(twf.Form):
    class child(twf.TableLayout):
        inline_engine_name = 'kajiki'
        template = '''
         <div  style="padding-top:20px">
<py:for each="c in w.children_hidden">
                ${c.display()}
            </py:for>
                            <div class="col-md-12 ks-section-name">
                                Recover password
                                <hr/>
                            </div>
        <div class="row">
            <div class="form-group col-md-4">
                ${w.children.password.display()}
                <span class="help-block" py:content="w.children.password.error_msg"/>
            </div>
        </div>
        <div class="row">
            <div class="form-group col-md-4">
                ${w.children.password_confirm.display()}
                <span class="help-block" py:content="w.children.password_confirm.error_msg"/>
        </div>
        </div>
        </div>

                '''
        data = HiddenField()
        password = PasswordField(label=l_('New password'), validator=Validator(required=True), css_class='form-control', placeholder=l_('New password'))
        password_confirm = PasswordField(label=l_('Confirm new password'), validator=Validator(required=True), css_class='form-control', placeholder=l_('Confirm password'))
        validator = FieldsMatch('password', 'password_confirm')

    submit = SubmitButton(css_class="btn btn-primary", value=l_("Save password"))

    action = lurl('/reset_request')


class UploadFileForm(twf.Form):
    class child(twf.TableLayout):
        inline_engine_name = 'kajiki'
        template = '''

            '''
        upload = FileField(label='')
    submit = SubmitButton(css_class="btn btn-primary", value=l_("Import"))
    action = lurl('/')
