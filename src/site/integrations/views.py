from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url="/user/login/")
def integrations(request):

    if request.method == 'GET':
        response = render(request, "integrations.html")
        response.set_signed_cookie("user", request.user.username)
        return response

    if request.method == 'POST':
        data = request.POST
        api = data.get('Conectar')

        if api == 'ifood':
            print("Conectando ao iFood...")
            return render(request, "integrations.html", {"ok": "Verifique o e-mail enviado pelo iFood."})