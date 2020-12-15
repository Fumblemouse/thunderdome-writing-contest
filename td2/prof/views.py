"""Views for registration, login and changes"""
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView
from django.urls import reverse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from prof.forms import Settingform, SignupForm, ChangeUsernameform, ChangePasswordform, ResetPasswordform, SetPasswordConfirm, ChangeEmailform
from prof.tokens import account_activation_token


@login_required
def profile(request, username=''):
    """Profile # Need Edit"""
    if username == '' and request.user.is_authenticated:
        return render(request, 'prof/profile.html',{'u':request.user.username})
    else:
        return render(request, 'prof/profile.html',{'u':username})


###### signin  #######
def signin(request):
    """signin routine"""
    if request.user.is_authenticated:
        return HttpResponseRedirect('/prof/profile/')
    elif request.method == 'GET':
        return render(request, 'prof/login.html',{})
    elif request.method == 'POST':
        try:
            emp = request.POST['email']
            pwp = request.POST['password']
            if '@' in emp:
                user = User.objects.get(email=emp)
            else:
                user = User.objects.get(username=emp)
            rea = authenticate(username=user.username, password=pwp)
            if rea is not None:
                login(request, rea)
                link = '/profile/'+str(rea)
                return HttpResponseRedirect(link)
            else:
                return render(request, 'prof/login.html', {'error_msg': 'Wrong Password or User not active'})
        except: # pylint: disable=bare-except
            return render(request, 'prof/login.html', {'error_msg': 'User not found'})

###### old signup deleted ##########

@login_required
def p_logout(request):
    """replacement logout function"""
    logout(request)
    return redirect('/login/')


@login_required
def settings(request):
    """Settings page"""
    if request.POST:
        form = Settingform(request.POST)

        if form.is_valid():
            form_user = User.objects.get(username=request.user.username)
            form = Settingform(request.POST, instance=form_user)
            messages.success(request, 'Your settings were updated successfully!')
            form.save()  # cleaned indenting, but would not save unless I added at least 6 characters.
            return redirect('profile')
        else:
            i = form.errors
            form_user = User.objects.get(username=request.user.username)
            form = Settingform(instance=form_user)
            return render(request, 'prof/settings.html', {'form': form, 'error_msg': i})
    else:
        form_user = User.objects.get(username=request.user.username)
        form = Settingform(instance=form_user)
        return render(request, 'prof/settings.html', {'form': form})


@login_required
def change_password(request):
    """change password"""
    if request.method == 'POST':
        form = ChangePasswordform(request.user, request.POST)
        form.fields['old_password'].widget = forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was updated successfully!')
            return redirect('/')
        else:
            return render(request, 'change-password.html', {'form': form, 'error_msg': form.errors})
    else:
        form = ChangePasswordform(request.user)
    return render(request, 'prof/change-password.html', {
        'form': form
    })

@login_required
def change_email(request):
    """change email"""
    if request.POST:
        form = ChangeEmailform(request.POST)
        if request.user.email == form.data['email']:
            messages.success(request, 'Your email hasn\'t changed!')
            return redirect('/')
        elif form.is_valid():
            form_user = User.objects.get(email=request.user.email)
            form = ChangeEmailform(request.POST, instance=form_user)
            form.save()  # cleaned indenting, but would not save unless I added at least 6 characters.
            messages.success(request, 'Your email was updated successfully!')
            return redirect('/')
        else:
            form_user = User.objects.get(email=request.user.email)
            form = ChangeEmailform(instance=form_user)
            return render(request, 'prof/change-email.html', {'form': form, 'error_msg': form.errors})
    else:
        form_user = User.objects.get(email=request.user.email)
        form = ChangeEmailform(instance=form_user)
        return render(request, 'prof/change-email.html', {'form': form})

@login_required
def change_username(request):
    """change username"""
    if request.POST:
        form = ChangeUsernameform(request.POST)
        #form.fields['usernaem'].value = request.user.username
        #print(request.user.username)
        #print(form.data['username'])
        #print(form.is_valid())
        if request.user.username == form.data['username']:
            messages.success(request, 'Your username hasn\'t changed!')
            return redirect('/')
        elif form.is_valid():
            form_user = User.objects.get(username=request.user.username)
            form = ChangeUsernameform(request.POST, instance=form_user)
            form.save()  # cleaned indenting, but would not save unless I added at least 6 characters.
            messages.success(request, 'Your username was updated successfully!')
            return redirect('/')
        else:
            form_user = User.objects.get(username=request.user.username)
            form = ChangeUsernameform(instance=form_user)
            return render(request, 'prof/change-username.html', {'form': form, 'error_msg': form.errors})
    else:
        form_user = User.objects.get(username=request.user.username)
        form = ChangeUsernameform(instance=form_user)
        return render(request, 'prof/change-username.html', {'form': form})

####### New Signup ######
def signup(request):
    """signup"""
    if request.user.is_authenticated:
        return HttpResponseRedirect('/prof/profile/')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            if User.objects.filter(email = form.data['email']).exists():
                form.add_error('email', 'Email already exists.')
                return render(request, 'prof/signup.html', {'form': form, 'error_msg':form.errors})
            user = form.save(commit=False)

            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('acc-active-email.html', {
                'user':user, 'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), #.decode()
                'token': account_activation_token.make_token(user),
            })
            # Sending activation link in terminal
            # user.email_user(subject, message)
            mail_subject = 'Activate your account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request, 'prof/confirm.html', {})
            #return HttpResponse('Please confirm your email address to complete the registration.')
            # return render(request, 'acc_active_sent.html')
    else:
        form = SignupForm()
    return render(request, 'prof/signup.html', {'form': form})


def activate(request, uidb64, token):
    """@DynamicAttrs"""
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Thank you for your email confirmation.')
        return redirect('/')
        #return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

#########    Password Reset Classes   ##########
class PassReset(PasswordResetView):
    """Pasword reset"""
    form_class = ResetPasswordform

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('/prof/profile/')
        else:
            return super().dispatch(*args, **kwargs)

class PassResetDone(PasswordResetDoneView):
    """Password reset done"""
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        reset_url = str(self.request.META.get('HTTP_REFERER'))[:-1]
        check = str(self.request.build_absolute_uri()).rsplit("/", 2)[0]
        if check != reset_url:
            return HttpResponseRedirect(reverse('home'))
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('/prof/profile/')
        else:
            return super().dispatch(*args, **kwargs)

class PassResetComplete(PasswordResetCompleteView):
    """password reset complete"""
    def dispatch(self, *args, **kwargs):
        reset_url = str(self.request.META.get('HTTP_REFERER')).rsplit("/", 3)[0]
        check = str(self.request.build_absolute_uri()).rsplit("/", 2)[0]
        if reset_url != check:
        #if 'reset' not in check:
            return HttpResponseRedirect(reverse('home'))
        else:
            return super().dispatch(*args, **kwargs)

class PassResetConfirm(PasswordResetConfirmView):
    """password resest confirm"""
    form_class = SetPasswordConfirm
