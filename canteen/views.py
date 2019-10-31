from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView,CreateView
from django.shortcuts import render

# Create your views here.
from django.contrib.auth import login, logout
from django.urls import reverse_lazy

from . import forms
class ThanksPage(TemplateView):
    template_name = 'thanks.html'

# class HomePage(TemplateView):
    # template_name = 'index.html'

class SignUp(CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy("login")
    template_name = "index.html"
