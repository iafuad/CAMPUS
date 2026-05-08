from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (
    LostAndFoundPost,
    LostAndFoundPhoto,
    # ClaimRequest,
    LostAndFoundStatus,
    # ClaimRequestStatus,
)
from .forms import LostAndFoundPostForm, ClaimRequestForm
from apps.media.models import Photo


def post_list(request):
    """View to display all active lost and found posts."""
    # Filter out soft-deleted posts
    posts = LostAndFoundPost.objects.filter(deleted_at__isnull=True).order_by(
        "-created_at"
    )

    # Assuming this (lost_found/post_list.html) will be created inside templates folder
    return render(request, "lost_found/post_list.html", {"posts": posts})


@login_required
def post_create(request):
    """View to create a new lost or found post with multiple photo uploads."""
    if request.method == "POST":
        form = LostAndFoundPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user

            # Provide a default status like 'Active' when someone creates a post
            status, _ = LostAndFoundStatus.objects.get_or_create(name="Active")
            post.status = status
            post.save()

            # Handle photo uploads using Photo model from media app
            for order, file in enumerate(form.cleaned_data.get("uploaded_photos", [])):
                photo = Photo.objects.create(file=file, uploaded_by=request.user)
                LostAndFoundPhoto.objects.create(post=post, photo=photo, order=order)

            messages.success(request, f"Successfully created your {post.type} post!")
            return redirect("lost_found:post_detail", post_id=post.id)
    else:
        form = LostAndFoundPostForm()

    return render(request, "lost_found/post_form.html", {"form": form})


def post_detail(request, post_id):
    """View to display a specific post and its claim form."""
    post = get_object_or_404(LostAndFoundPost, id=post_id, deleted_at__isnull=True)
    claim_form = ClaimRequestForm()

    # Assuming this (lost_found/post_detail.html) will be created inside templates folder
    return render(
        request,
        "lost_found/post_detail.html",
        {"post": post, "claim_form": claim_form},
    )


@login_required
def submit_claim(request, post_id):
    """Submit a claim for a specific item/post."""
    post = get_object_or_404(LostAndFoundPost, id=post_id, deleted_at__isnull=True)

    if request.method == "POST":
        form = ClaimRequestForm(request.POST)
        if form.is_valid():
            # TODO: Implement claim logic with LostAndFoundMatch
            messages.info(
                request,
                "Claim functionality is under development. Please contact the item owner.",
            )
            return redirect("lost_found:post_detail", post_id=post.id)

    return redirect("lost_found:post_detail", post_id=post_id)
