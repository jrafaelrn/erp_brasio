from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url="/user/login/")
def integrations(request):
    return render(request, "integrations.html")
 