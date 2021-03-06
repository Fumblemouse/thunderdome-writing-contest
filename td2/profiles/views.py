"""Views for profiles app
"""
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
from promptarena.models import Contest
from .forms import SignUpForm, UserUpdateForm


logger = logging.getLogger(__name__)


UserModel = get_user_model()


def set_timezone(request):
    """replacement login function"""
    if request.user.is_authenticated:
        request.session['django_timezone'] = request.user.timezone
        # Redirect to a success page.
        messages.success(request, 'Welcome, ' + request.user.username + "!")
        return redirect(reverse('home'))
    else:
        messages.warning(request, 'You have failed to provide a valid username or password')
    return redirect(reverse('login'))


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
    if request.method != 'POST':
        return render(request, 'registration/activate.html', {})
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

@login_required
def settings(request):
    """user sets their own settings"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST,instance=request.user)
        if user_form.is_valid():
            user_form_uncommitted = user_form.save(commit=False)
            user_form_uncommitted.timezone = request.POST['timezone']
            user_form_uncommitted.save()
            request.session['django_timezone'] = request.POST['timezone']
            messages.success(request,'Your Profile has been updated!')
            stories = Story.objects.filter(
                author = request.user
            )
            story_num = 0
            for story in stories:
                if story.access > request.user.highest_access:
                    story.access = request.user.highest_access
                    story_num += 1

            if story_num:
                messages.success(request, 'You have updated ' + str(story_num) + ' story permissions')

            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)

    context={'user_form': user_form, 'timezones': common_timezones}
    return render(request, 'profiles/settings.html',context )



@login_required
def profile(request):
    """Show profile"""
    context = {
        'user_context': request.user,
        'fields_context' : {
            'Username' : request.user.username,
            'Email' : request.user.email,
            'First name': request.user.first_name,
            'Last name' : request.user.last_name,
            'Bio': request.user.bio,
            'Time zone' : request.user.timezone,
            'Highest access level' : request.user.get_highest_access_display()
        }
    }

    stories_context = Story.objects.filter(
        author = request.user.pk
    )

    contests_context = Contest.objects.filter(
        creator = request.user.pk
    )
    context['stories_context'] = stories_context
    context['contests_context'] = contests_context
    return render(request, 'profiles/profile.html', context)


@login_required
def p_logout(request):
    """replacement logout function"""
    logout(request)
    messages.success(request, 'You have managed to logout. Byeeee!')
    return redirect(reverse('home'))
