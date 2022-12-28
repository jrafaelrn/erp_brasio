from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail




@login_required(login_url="/user/login/")
def integrations(request):

    if request.method == 'GET':
        response = render(request, "integrations.html")
        response.set_signed_cookie("user", request.user.username)
        return response

    if request.method == 'POST':
        #integration_request(request)
        return manual_integration(request)
    

# Make a request to the API Supplier 
# to get access to data user
def integration_request(request):
    
    data = request.POST
    api = data.get('Conectar')

    apis = connectAPI(api)
    api_return = apis.run()    
    
    if api_return:
        return render(request, "integrations.html", {"ok": "Verifique seu e-mail."})
    
    return render(request, "integrations.html", {"error": "Erro ao conectar."})



def manual_integration(request):
    
    mailer = import_mailer()    
    #mailer.send_email(request)
    username = request.get_signed_cookie("username")
    api = request.POST.get('Conectar')
    
    send_email_credentials_request(username, api, 'tec@luaempresas.com')
    
    response = render(request, "integrations.html")
    response.set_cookie(f"status_{api}", "Processando...", expires=60*60*24*30*60)
    
    return response 



def import_mailer():
    import os
    import sys
    
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_dir + '/tools')
    import mailer as mail
    return mail
    


def send_email_credentials_request(username:str, api:str, to:str):    
    
    try:
        subject = 'New credentials request'
        message = f'User {username} requested new credentials for {api}'
        recipient_list = [to]
        
        send_mail(subject, message, recipient_list)
        print('Email sent!')
    
    except Exception as e:
        print(f'Error sending email: {e}')
        pass   

