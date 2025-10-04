from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.contrib.auth import login
from django.urls import reverse_lazy
from .models import User
from .forms import CustomUserCreationForm


class RegisterView(CreateView):
    """
    User registration view.
    Converted from RegisterController in Laravel.
    """
    model = User
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)
