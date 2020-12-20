"""Views for Prof app"""
from django.contrib.auth import  logout
from django.contrib.auth import get_user_model
#from django.contrib.auth.models import User
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
#from .tokens import account_activation_token
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm

UserModel = get_user_model()




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
                return render(request, 'prof/signup.html', {'form': form, 'error_msg':form.errors})
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
            """
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            """
            messages.success(request, 'An email has been sent to your address. Click the link to complete the process ')
            return redirect('home')

    return render(request, 'registration/sign-up.html', {'form': form})

def activate(request, uidb64, token):
    """activate account after email response"""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,'Thank you for your email confirmation. Now you can login your account.')
    else:
        messages.error(request,'Activation link is invalid!')
    return redirect('home')


@login_required
def settings(request):
    """user sets their own settings"""
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST,instance=request.user.profile)
        u_form = UserUpdateForm(request.POST,instance=request.user)
        if p_form.is_valid() and u_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,'Your Profile has been updated!')
            return redirect('profile')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)
        u_form = UserUpdateForm(instance=request.user)

    context={'p_form': p_form, 'u_form': u_form}
    return render(request, 'prof/settings.html',context )



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
            'Show profile and work publically?' : request.user.profile.public_profile
        }
    }
    return render(request, 'prof/profile.html', context)


@login_required
def p_logout(request):
    """replacement logout function"""
    logout(request)
    messages.success(request, 'You have managed to logout. Byeeee!')
    return redirect(reverse('home'))
