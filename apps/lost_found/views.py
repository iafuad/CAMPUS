from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import lost_and_found_post, claim_request, lost_and_found_status, claim_request_status
from .forms import LostAndFoundPostForm, ClaimRequestForm
from apps.media.models import Photo

def post_list(request):
    """View to display all active lost and found posts."""
    # Filter out soft-deleted posts
    posts = lost_and_found_post.objects.filter(deleted_at__isnull=True).order_by('-created_at')
    
    # Assuming this (lost_found/post_list.html) will be created inside templates folder
    return render(request, 'lost_found/post_list.html', {
        'posts': posts
    })

@login_required
def post_create(request):
    """View to create a new lost or found post with multiple photo uploads."""
    if request.method == 'POST':
        form = LostAndFoundPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            
            # Provide a default status like 'Active' when someone creates a post
            status, created = lost_and_found_status.objects.get_or_create(
                status_id=1, 
                defaults={'status_name': 'Active'}
            )
            post.lost_and_found_status = status
            post.save()
            
            # Loop through uploaded photos and link them to the post
            for file in request.FILES.getlist('uploaded_photos'):
                photo = Photo.objects.create(file=file, uploaded_by=request.user)
                post.photos.add(photo)
                
            messages.success(request, f"Successfully created your {post.type} post!")
            # Assuming you name the url route 'lost_found_post_detail'
            return redirect('lost_found_post_detail', post_id=post.post_id)
    else:
        form = LostAndFoundPostForm()
        
    # Assuming this (lost_found/post_form.html) will be created inside templates folder
    return render(request, 'lost_found/post_form.html', {'form': form})

def post_detail(request, post_id):
    """View to display a specific post and its claim form."""
    post = get_object_or_404(lost_and_found_post, post_id=post_id, deleted_at__isnull=True)
    claim_form = ClaimRequestForm()
    
    # Assuming this (lost_found/post_detail.html) will be created inside templates folder
    return render(request, 'lost_found/post_detail.html', {
        'post': post,
        'claim_form': claim_form
    })

@login_required
def submit_claim(request, post_id):
    """Submit a claim for a specific item/post."""
    post = get_object_or_404(lost_and_found_post, post_id=post_id, deleted_at__isnull=True)
    
    if request.method == 'POST':
        form = ClaimRequestForm(request.POST)
        if form.is_valid():
            # Check if user already claimed this
            existing_claim = claim_request.objects.filter(user=request.user, lost_and_found_post=post).exists()
            if existing_claim:
                messages.warning(request, "You have already submitted a claim for this item.")
                return redirect('lost_found_post_detail', post_id=post.post_id)

            claim = form.save(commit=False)
            claim.user = request.user
            claim.lost_and_found_post = post
            
            # Default status to 'Pending'
            c_status, _ = claim_request_status.objects.get_or_create(
                claim_request_status_id=1,
                defaults={'claim_request_status_name': 'Pending'}
            )
            claim.claim_request_status = c_status
            claim.save()
            
            messages.success(request, "Your claim request has been successfully submitted.")
            return redirect('lost_found_post_detail', post_id=post.post_id)
            
    return redirect('lost_found_post_detail', post_id=post_id)