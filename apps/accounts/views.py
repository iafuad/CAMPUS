from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import RegisterForm, User


@login_required
def profile_view(request, handle):
    profile_user = get_object_or_404(User, handle=handle)

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": profile_user,
        },
    )


@login_required
def myself(request):
    return redirect("profile", handle=request.user.handle)


def register(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("login")

    return render(request, "accounts/register.html", {"form": form})
