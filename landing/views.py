from django.shortcuts import render

# Pagina principal
def index(request):
    return render(request, 'index.html')

def aboutUs(request):
    return render(request, 'aboutUs.html')    
