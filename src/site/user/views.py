from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django

def login(request):

    if request.method == 'GET':
        return render(request, "login.html")

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')  

        user = authenticate(request, username=username, password=password)   

        if user:
            login_django(request, user)
            return redirect('integrations')

        return render(request, "login.html", {"error": "Usuário ou senha inválidos."})