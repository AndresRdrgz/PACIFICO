from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import UserProfileForm, UserForm
from ..models import UserProfile
from django.contrib import messages

@login_required
def edit_profile(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Perfil actualizado exitosamente!')
            return redirect('edit_profile')
        else:
            messages.error(request, 'Por favor corrija los errores a continuación.')
            # Add form errors to messages for debugging
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=user_profile)
        

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })