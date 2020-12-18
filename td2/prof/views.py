from django.contrib.auth import login, authenticate, logout
#from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.email = form.cleaned_data.get('email')
            user.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'You have managed to sign up. /golfclap.')
            return redirect('home')

    return render(request, 'registration/sign-up.html', {'form': form})


@login_required
def profile(request):
    """Show profile"""
    return redirect(reverse('home'))


@login_required
def p_logout(request):
    """replacement logout function"""
    logout(request)
    messages.success(request, 'You have managed to logout. Byeeee!')
    return redirect(reverse('home'))


