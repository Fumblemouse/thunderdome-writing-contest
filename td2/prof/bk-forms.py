"""Forms for user registration, login, and change"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User







class Settingform(forms.ModelForm):
    """Settingform"""
    def __init__(self, *args, **kwargs):
        super(Settingform, self).__init__(*args, **kwargs)
        #self.fields['username'].required = True
        self.fields['first_name'].widget = forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        )
        self.fields['last_name'].widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )

    class Meta:
        model = User
        fields = ('first_name', 'last_name',)
        #fields = ('first_name', 'last_name',)


################################################################################

class SignupForm(UserCreationForm):
    """Signup form"""
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={
                'class': 'form-control'
                }
            )
        self.fields['username'].widget = forms.TextInput(
            attrs={
                'class': 'form-control'
                }
            )
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={
                'class': 'form-control'
                }
            )
        self.fields['password1'].required = True
        self.fields['password2'].required = True
    email = forms.EmailField(max_length=200, help_text='Required', required=True, widget=forms.TextInput(
            attrs={
                'class': 'form-control'
                }
            ))
    first_name = forms.CharField(max_length=30, help_text='Optional', required=False, widget=forms.TextInput(
            attrs={
                'class': 'form-control'
                }
            ))
    last_name = forms.CharField(max_length=30, help_text='Optional', required=False, widget=forms.TextInput(
            attrs={
                'class': 'form-control'
                }
            ))
    number = forms.IntegerField( max_value=99999999999999999999,required=False, widget=forms.TextInput(
            attrs={
                'type':'tel',
                'pattern':'[0-9]{10}',
                'class': 'form-control'
                }
            ))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2','first_name', 'last_name', )

############################################################################################

class ChangeUsernameform(forms.ModelForm):
    """Change userforms"""
    def __init__(self, *args, **kwargs):
        super(ChangeUsernameform, self).__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['username'].help_text = '<small id="emailHelp" class="form-text text-muted">Required. 150 characters or fewer. Letters, digits and ./+/-/_ only.</small>'

        self.fields['username'].widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )

    class Meta:
        model = User
        fields = ('username',)

class ChangeEmailform(forms.ModelForm):
    """Change emailforms"""
    def __init__(self, *args, **kwargs):
        super(ChangeEmailform, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

        self.fields['email'].widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )

    class Meta:
        model = User
        fields = ('email',)

class ChangePasswordform(PasswordChangeForm):
    """Change password form"""
    def __init__(self, *args, **kwargs):
        super(ChangePasswordform, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
        self.fields['new_password1'].widget = forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
        self.fields['new_password2'].widget = forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )

    class Meta:
        model = User
        fields= ('old_password', 'new_password1', 'new_password2')

class ResetPasswordform(PasswordResetForm):
    """ResetPasswordform"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
    class Meta:
        model = User
        fields= ('email')

class SetPasswordConfirm(SetPasswordForm):
    """SetPasswordConfirm"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget = forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
        self.fields['new_password2'].widget = forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
    class Meta:
        model = User
        fields= ('new_password1', 'new_password2')
