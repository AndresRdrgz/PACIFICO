from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import UserProfileForm, UserForm
from ..models import UserProfile
from django.contrib import messages

@login_required
def edit_profile(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('edit_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=user_profile)
        

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })