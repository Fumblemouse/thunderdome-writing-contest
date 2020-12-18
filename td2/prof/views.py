"""Views for Prof app"""
from django.contrib.auth import login, authenticate, logout
#from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm



def sign_up(request):
    """Sign up process"""
    #You can't sign up if you are logged in
    if request.user.is_authenticated:
        return redirect('profile')
    #grab POST form or create form as empty
    form = SignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.bio = form.cleaned_data.get('bio')
            user.profile.public_profile = form.cleaned_data.get('public_profile')
            user.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'You have managed to sign up. /golfclap.')
            return redirect('home')

    return render(request, 'registration/sign-up.html', {'form': form})

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
    return render(request, 'prof/profile.html', {})


@login_required
def p_logout(request):
    """replacement logout function"""
    logout(request)
    messages.success(request, 'You have managed to logout. Byeeee!')
    return redirect(reverse('home'))
