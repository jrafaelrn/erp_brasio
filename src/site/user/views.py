from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth import logout as logout_django


def login(request):

    if request.method == 'GET':
        response = render(request, "login.html")
        response.set_signed_cookie("login_user", "True")
        return response

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')  

        user = authenticate(request, username=username, password=password)   

        if user:
            login_django(request, user)
            ip = get_ip_address(request)
            print(f'User {username} logged in from {ip}')
            return redirect('integrations')

        return render(request, "login.html", {"error": "Usuário ou senha inválidos."})
    

def logout(request):
    
    logout_django(request)
    ip = get_ip_address(request)
    print(f'User {request.user.username} logged out from {ip}')
    return redirect('login')
    


def get_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip