from django.shortcuts import render

from django.http import HttpResponse


def forum_index(request):
    return HttpResponse("Hello, world. You're at the forum index.")
