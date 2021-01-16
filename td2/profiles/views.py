"""Views for Profiles app"""
import logging
from django.contrib.auth import  logout
from django.contrib.auth import get_user_model

from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from pytz import common_timezones
from baseapp.models import Story
from promptarena.models import Prompt
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm


logger = logging.getLogger(__name__)


UserModel = get_user_model()


def set_timezone(request):
    """replacement login function"""
    if request.user.is_authenticated:
        request.session['django_timezone'] = request.user.profile.timezone
        # Redirect to a success page.
        messages.success(request, 'Welcome, ' + request.user.username + "!")
        return redirect(reverse('home'))
    else:
        messages.warning(request, 'You have failed to provide a valid username or password')
    return render(request, 'registration/login.html', {})


def sign_up(request):
    """Sign up process"""
    #You can't sign up if you are logged in
    if request.user.is_authenticated:
        return redirect('profile')
    #grab POST form or create form as empty
    form = SignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            """TODO add email restriction for production
            if User.objects.filter(email = form.data['email']).exists():
                form.add_error('email', 'Email already exists.')
                return render(request, 'profile/signup.html', {'form': form, 'error_msg':form.errors})
                """
            #don't commit user until validation has occured
            user = form.save(commit=False)
            #user.refresh_from_db()
            user.is_active = False
            user.save()
            user.profile.bio = form.cleaned_data.get('bio')
            user.profile.public_profile = form.cleaned_data.get('public_profile')
            current_site = get_current_site(request)
            mail_subject = 'Enter the Thunderdome'
            message = render_to_string('registration/acc-active-email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            """#Include to auto-signin
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            """
            messages.success(request, 'An email has been sent to your specificed address. Click the link contained within it to complete the process ')
            return redirect('home')

    return render(request, 'registration/sign-up.html', {'form': form})

def activate(request, uidb64, token):
    """activate account after email response"""
    if request.method == 'POST':
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token) and not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request,'Thank you for your email confirmation. Now you can login your account.')
        else:
            messages.error(request,'Activation link is invalid!')
        return render(request, 'baseapp/home.html',{} )
    return render(request, 'registration/activate.html', {})

@login_required
def settings(request):
    """user sets their own settings"""
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST,instance=request.user.profile)
        user_form = UserUpdateForm(request.POST,instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form_uncommitted = profile_form.save(commit=False)
            profile_form_uncommitted.timezone = request.POST['timezone']
            profile_form_uncommitted.save()
            request.session['django_timezone'] = request.POST['timezone']
            messages.success(request,'Your Profile has been updated!')
            return redirect('profile')
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        user_form = UserUpdateForm(instance=request.user)

    context={'profile_form': profile_form, 'user_form': user_form, 'timezones': common_timezones}
    return render(request, 'profiles/settings.html',context )



@login_required
def profile(request):
    """Show profile"""
    context = {
        'user_context': request.user,
        'profile_context' : request.user.profile,
        'fields_context' : {
            'Username' : request.user.username,
            'Email' : request.user.email,
            'First name': request.user.first_name,
            'Last name' : request.user.last_name,
            'Bio': request.user.profile.bio,
            'Time zone' : request.user.profile.timezone,
            'Show work publically?' : request.user.profile.public_profile
        }
    }

    stories_context = Story.objects.filter(
        author = request.user.pk
    )

    prompts_context = Prompt.objects.filter(
        creator = request.user.pk
    )
    context['stories_context'] = stories_context
    context['prompts_context'] = prompts_context
    return render(request, 'profiles/profile.html', context)


@login_required
def p_logout(request):
    """replacement logout function"""
    logout(request)
    messages.success(request, 'You have managed to logout. Byeeee!')
    return redirect(reverse('home'))
    