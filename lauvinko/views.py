from django.shortcuts import render


def react_index(request):
    return render(request, 'react_index.html')
