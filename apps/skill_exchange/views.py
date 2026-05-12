from django.contrib import messages                 
from django.db import transaction                  
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
from datetime import timedelta

from .forms import SkillExchangePostForm
from .signals import find_and_create_matches
from .models import (
    MatchDecision,
    ExchangePost,
    ExchangeMatch,
    ExchangeSession,
    SessionEndRequest,
    SessionFeedback,
)
from apps.threads.models import Thread, ThreadParticipant
from apps.common.choices import (
    ExchangeMatchStatus,
    ExchangePostStatus,
    ExchangeSessionStatus,
    MatchDecisionStatus,
    ThreadVisibility,
    ThreadParticipantRole,
    SessionEndRequestStatus,
    SessionFeedbackStatus,
)

@login_required
def post_list(request):
    # Get all posts by the current user (both active and completed)
    posts = ExchangePost.objects.filter(
        author=request.user,
    ).order_by("-created_at")

    return render(request, "skill_exchange/post_list.html", {"posts": posts})

@login_required
def post_create(request):
    if request.method == "POST":
        form = SkillExchangePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()                  # skills attached first
            find_and_create_matches(post)    # then match
            return redirect("skill_exchange:post_list")
    else:
        form = SkillExchangePostForm()
    return render(request, "skill_exchange/post_form.html", {"form": form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(ExchangePost, pk=post_id, author=request.user)
    form = SkillExchangePostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save()
        find_and_create_matches(post)        # re-run matching after skills change
        return redirect("skill_exchange:post_list")
    return render(request, "skill_exchange/post_form.html", {"form": form, "post": post})


@login_required
def match_list(request):
    """Display matches for the user's posts, filtered by status"""
    # Get all matches where user's posts are involved
    base_queryset = ExchangeMatch.objects.filter(
        Q(ex_p_a__author=request.user) | Q(ex_p_b__author=request.user)
    ).select_related('ex_p_a', 'ex_p_b', 'ex_p_a__author', 'ex_p_b__author')

    # Filter by status
    pending_matches = base_queryset.filter(status=ExchangeMatchStatus.PENDING).order_by("-matched_at")
    matched_matches = base_queryset.filter(status=ExchangeMatchStatus.MATCHED).order_by("-matched_at")
    closed_matches = base_queryset.filter(status=ExchangeMatchStatus.CLOSED).order_by("-matched_at")

    context = {
        "pending_matches": pending_matches,
        "matched_matches": matched_matches,
        "closed_matches": closed_matches,
        "user": request.user,
    }
    return render(request, "skill_exchange/match_list.html", context)


@login_required
def match_detail(request, match_id):
    """Display a specific match"""
    match = get_object_or_404(ExchangeMatch, id=match_id)

    # Check if user is involved in this match
    if not (match.ex_p_a.author == request.user or match.ex_p_b.author == request.user):
        return redirect("skill_exchange:match_list")

    # Determine which post belongs to current user
    if match.ex_p_a.author == request.user:
        user_post = match.ex_p_a
        other_post = match.ex_p_b
        other_user = match.ex_p_b.author
    else:
        user_post = match.ex_p_b
        other_post = match.ex_p_a
        other_user = match.ex_p_a.author

    # Find common skills (user offers, other requests AND user requests, other offers)
    user_offered_other_needs = user_post.skills_offered.filter(
        id__in=other_post.skills_needed.values('id')
    )

    user_needed_other_offers = user_post.skills_needed.filter(
       id__in=other_post.skills_offered.values('id')
    )

    # Try to fetch the session if both users have accepted
    session = None
    if match.status == ExchangeMatchStatus.MATCHED:
        session = ExchangeSession.objects.filter(match=match).first()

    # Check if current user has made a decision on this match
    user_decision = MatchDecision.objects.filter(
        exchange_match=match,
        decided_by=request.user,
    ).first()

    context = {
        "match": match,
        "user_post": user_post,
        "other_post": other_post,
        "other_user": other_user,
        "user_offered_other_needs": user_offered_other_needs,
        "user_needed_other_offers": user_needed_other_offers,
        "session": session,
        "user_decision": user_decision,
    }
    return render(request, "skill_exchange/match_detail.html", context)

@login_required
def match_decision(request, match_id):
    """
    Called when a user accepts or rejects a match.
    Both users must accept for the session + thread to be created.
    If either rejects, the match is closed immediately.
    """
    match = get_object_or_404(ExchangeMatch, pk=match_id)

    # Make sure the requesting user is actually part of this match
    user_post = None
    other_post = None

    if match.ex_p_a.author == request.user:
        user_post  = match.ex_p_a
        other_post = match.ex_p_b
    elif match.ex_p_b.author == request.user:
        user_post  = match.ex_p_b
        other_post = match.ex_p_a
    else:
        messages.error(request, "You are not part of this match.")
        return redirect("skill_exchange:match_list")

    # Don't allow decisions on already-closed matches
    if match.status != ExchangeMatchStatus.PENDING:
        messages.error(request, "This match is no longer pending.")
        return redirect("skill_exchange:match_detail", match_id=match_id)

    # Prevent the same user from deciding twice
    already_decided = MatchDecision.objects.filter(
        exchange_match=match,
        decided_by=request.user,
    ).exists()

    if already_decided:
        messages.warning(request, "You have already responded to this match.")
        return redirect("skill_exchange:match_detail", match_id=match_id)

    if request.method == "POST":
        action = request.POST.get("action")  # "accept" or "reject"

        if action not in ("accept", "reject"):
            messages.error(request, "Invalid action.")
            return redirect("skill_exchange:match_detail", match_id=match_id)

        with transaction.atomic():
            if action == "reject":
                # Record the decision
                MatchDecision.objects.create(
                    exchange_match=match,
                    decided_by=request.user,
                    status=MatchDecisionStatus.REJECTED,
                )
                # Close the match immediately — no thread created
                match.status = ExchangeMatchStatus.CLOSED
                match.save(update_fields=["status"])

                messages.info(request, "Match rejected.")
                return redirect("skill_exchange:match_list")

            # action == "accept"
            MatchDecision.objects.create(
                exchange_match=match,
                decided_by=request.user,
                status=MatchDecisionStatus.ACCEPTED,
            )

            # Check if the OTHER user has also accepted
            other_accepted = MatchDecision.objects.filter(
                exchange_match=match,
                decided_by=other_post.author,
                status=MatchDecisionStatus.ACCEPTED,
            ).exists()

            if not other_accepted:
                # Waiting for the other user — nothing else to do yet
                messages.success(request, "You accepted. Waiting for the other user.")
                return redirect("skill_exchange:match_detail", match_id=match_id)

            # --- BOTH USERS ACCEPTED --- create session + thread ---

            # 1. Update match status
            match.status = ExchangeMatchStatus.MATCHED
            match.save(update_fields=["status"])

            # 2. Mark both posts as matched so they stop appearing in search
            match.ex_p_a.status = ExchangePostStatus.MATCHED
            match.ex_p_a.save(update_fields=["status"])
            match.ex_p_b.status = ExchangePostStatus.MATCHED
            match.ex_p_b.save(update_fields=["status"])

            # 3. Create the private thread (same pattern as your lost_found)
            thread = Thread.objects.create(
                title=f"{match.ex_p_a.author.handle} ↔ {match.ex_p_b.author.handle}",
                description=(
                    f"Private session for match #{match.pk}. "
                    f"Use this to coordinate your skill exchange."
                ),
                visibility=ThreadVisibility.PRIVATE,
            )
            ThreadParticipant.objects.create(
                thread=thread,
                user=match.ex_p_a.author,
                role=ThreadParticipantRole.AUTHOR,
            )
            ThreadParticipant.objects.create(
                thread=thread,
                user=match.ex_p_b.author,
                role=ThreadParticipantRole.MEMBER,
            )

            # 4. Create the ExchangeSession linked to match + thread
            session = ExchangeSession.objects.create(
                match=match,
                thread=thread,
                status=ExchangeSessionStatus.PENDING,
            )

            # TODO — notify both users:
            # notify_user(recipient=match.ex_p_a.author, verb="match_accepted", target=session)
            # notify_user(recipient=match.ex_p_b.author, verb="match_accepted", target=session)

        messages.success(
            request,
            "Both users accepted! A private session thread has been created.",
        )
        return redirect("skill_exchange:session_detail", session_id=session.pk)

    # GET — confirmation page showing match details before deciding
    return render(request, "skill_exchange/match_decision.html", {
        "match":      match,
        "user_post":  user_post,
        "other_post": other_post,
    })


@login_required
def session_detail(request, session_id):
    """Display a skill exchange session with its thread"""
    session = get_object_or_404(ExchangeSession, pk=session_id)
    
    # Check if user is part of the match
    if not (session.match.ex_p_a.author == request.user or session.match.ex_p_b.author == request.user):
        messages.error(request, "You are not part of this session.")
        return redirect("skill_exchange:match_list")
    
    # Get the thread
    thread = session.thread
    
    # Handle POST request for new messages (only if session is not completed)
    if request.method == "POST":
        # Prevent messaging on completed sessions
        if session.status == ExchangeSessionStatus.COMPLETED:
            messages.error(request, "This session is completed. No new messages can be sent.")
            return redirect("skill_exchange:session_detail", session_id=session_id)
        
        from django.db import transaction as db_transaction
        from apps.media.models import Photo
        from apps.threads.models import ThreadMessage, MessageAttachment
        
        content = request.POST.get("content", "").strip()
        files = request.FILES.getlist("photos")
        
        if content:
            with db_transaction.atomic():
                msg = ThreadMessage.objects.create(
                    thread=thread,
                    sender=request.user,
                    content=content,
                )
                
                for idx, f in enumerate(files):
                    photo = Photo.objects.create(file=f, uploaded_by=request.user)
                    MessageAttachment.objects.create(
                        message=msg, photo=photo, order=idx
                    )
        
        return redirect("skill_exchange:session_detail", session_id=session_id)
        
        return redirect("skill_exchange:session_detail", session_id=session_id)
    
    participants = thread.participants.all()
    messages_in_thread = thread.messages.select_related("sender").prefetch_related("attachments__photo").order_by('sent_at')
    
    # Add show_timestamp logic: only show if sender changed or 30+ mins since last message from same sender
    processed_messages = []
    for idx, msg in enumerate(messages_in_thread):
        show_timestamp = True
        
        if idx > 0:
            prev_msg = processed_messages[idx - 1]
            # If same sender as previous message, check time difference
            if prev_msg['message'].sender == msg.sender:
                time_diff = msg.sent_at - prev_msg['message'].sent_at
                if time_diff < timedelta(minutes=30):
                    show_timestamp = False
        
        processed_messages.append({
            'message': msg,
            'show_timestamp': show_timestamp
        })
    
    context = {
        "session": session,
        "thread": thread,
        "participants": participants,
        "messages": processed_messages,
        "match": session.match,
        "is_session_completed": session.status == ExchangeSessionStatus.COMPLETED,
    }
    return render(request, "skill_exchange/session_detail.html", context)


# @login_required
# def session_end_request(request, session_id):
#     """User requests to end a session"""
#     session = get_object_or_404(ExchangeSession, pk=session_id)
    
#     # Check if user is part of the session
#     if not (session.match.ex_p_a.author == request.user or session.match.ex_p_b.author == request.user):
#         messages.error(request, "You are not part of this session.")
#         return redirect("skill_exchange:match_list")
    
#     # Session must be active or pending to end it
#     if session.status not in [ExchangeSessionStatus.PENDING, ExchangeSessionStatus.ACTIVE]:
#         messages.error(request, "This session cannot be ended.")
#         return redirect("skill_exchange:session_detail", session_id=session_id)
    
#     # Check if there's already a pending end request
#     pending_request = SessionEndRequest.objects.filter(
#         exchange_session=session,
#         status=SessionEndRequestStatus.PENDING,
#     ).first()
    
#     if pending_request and pending_request.requested_by == request.user:
#         messages.warning(request, "You have already requested to end this session.")
#         return redirect("skill_exchange:session_detail", session_id=session_id)
    
#     if pending_request and pending_request.requested_by != request.user:
#         # Other user already requested to end - show confirmation page
#         return render(request, "skill_exchange/session_end_confirm.html", {
#             "session": session,
#             "end_request": pending_request,
#             "action": "approve",
#         })
    
#     if request.method == "POST":
#         with transaction.atomic():
#             # Create end request
#             end_request = SessionEndRequest.objects.create(
#                 exchange_session=session,
#                 requested_by=request.user,
#                 status=SessionEndRequestStatus.PENDING,
#             )
        
#         messages.success(request, "End session request sent. Waiting for other user to respond.")
#         return redirect("skill_exchange:session_detail", session_id=session_id)
    
#     # Show confirmation page to create end request
#     return render(request, "skill_exchange/session_end_confirm.html", {
#         "session": session,
#         "action": "request",
#     })


# @login_required
# def session_end_decision(request, session_id):
#     """Other user approves or denies the end request"""
#     session = get_object_or_404(ExchangeSession, pk=session_id)
    
#     if not (session.match.ex_p_a.author == request.user or session.match.ex_p_b.author == request.user):
#         messages.error(request, "You are not part of this session.")
#         return redirect("skill_exchange:match_list")
    
#     end_request = SessionEndRequest.objects.filter(
#         exchange_session=session,
#         status=SessionEndRequestStatus.PENDING,
#     ).first()
    
#     if not end_request:
#         messages.error(request, "No pending end request for this session.")
#         return redirect("skill_exchange:session_detail", session_id=session_id)
    
#     if end_request.requested_by == request.user:
#         messages.warning(request, "You cannot respond to your own end request.")
#         return redirect("skill_exchange:session_detail", session_id=session_id)
    
#     if request.method == "POST":
#         action = request.POST.get("action")
        
#         if action not in ("approve", "deny"):
#             messages.error(request, "Invalid action.")
#             return redirect("skill_exchange:session_detail", session_id=session_id)
        
#         with transaction.atomic():
#             if action == "approve":
#                 end_request.status = SessionEndRequestStatus.APPROVED
#                 end_request.responded_at = timezone.now()
#                 end_request.save(update_fields=["status", "responded_at"])
                
#                 session.status = ExchangeSessionStatus.COMPLETED
#                 session.ended_at = timezone.now()
#                 session.save(update_fields=["status", "ended_at"])
                
#                 messages.success(request, "Session ended. You can now provide feedback from the match details.")
#                 # CHANGED: Redirect back to match details instead of feedback form
#                 return redirect("skill_exchange:match_detail", match_id=session.match.id)
#             else:
#                 end_request.status = SessionEndRequestStatus.DENIED
#                 end_request.responded_at = timezone.now()
#                 end_request.save(update_fields=["status", "responded_at"])
                
#                 messages.info(request, "End request denied. The session continues.")
#                 return redirect("skill_exchange:session_detail", session_id=session_id)
    
#     return render(request, "skill_exchange/session_end_confirm.html", {
#         "session": session,
#         "end_request": end_request,
#         "action": "respond",
#     })


# @login_required
# def session_feedback_form(request, session_id):
#     """Form to give feedback after session ends"""
#     session = get_object_or_404(ExchangeSession, pk=session_id)
    
#     # Check if user is part of the session
#     if not (session.match.ex_p_a.author == request.user or session.match.ex_p_b.author == request.user):
#         messages.error(request, "You are not part of this session.")
#         return redirect("skill_exchange:match_list")
    
#     # Session must be completed
#     if session.status != ExchangeSessionStatus.COMPLETED:
#         messages.error(request, "Cannot submit feedback for an incomplete session.")
#         return redirect("skill_exchange:session_detail", session_id=session_id)
    
#     # Get the end request to check who initiated
#     end_request = SessionEndRequest.objects.filter(
#         exchange_session=session,
#         status=SessionEndRequestStatus.APPROVED,
#     ).first()
    
#     if not end_request:
#         messages.error(request, "No approved end request found.")
#         return redirect("skill_exchange:session_detail", session_id=session_id)
    
#     # Check if current user initiated the end request
#     user_initiated_end = (end_request.requested_by == request.user)
    
#     # Determine who the other user is
#     if session.match.ex_p_a.author == request.user:
#         other_user = session.match.ex_p_b.author
#         user_post = session.match.ex_p_a
#         other_post = session.match.ex_p_b
#     else:
#         other_user = session.match.ex_p_a.author
#         user_post = session.match.ex_p_b
#         other_post = session.match.ex_p_a
    
#     # Get feedback from the other user to check if they already gave feedback
#     other_user_feedback = SessionFeedback.objects.filter(
#         exchange_session=session,
#         rated_by_user=other_user,
#     ).first()
    
#     # If current user initiated the end request, they can only give feedback after other user has
#     if user_initiated_end and not other_user_feedback:
#         return render(request, "skill_exchange/session_feedback_pending.html", {
#             "session": session,
#             "other_user": other_user,
#             "reason": "initiated",  # User initiated the end request
#         })
    
#     # Check if current user already gave feedback
#     existing_feedback = SessionFeedback.objects.filter(
#         exchange_session=session,
#         rated_by_user=request.user,
#     ).first()
    
#     if request.method == "POST":
#         rating = request.POST.get("rating")
#         comment = request.POST.get("comment", "").strip()
        
#         if not rating:
#             messages.error(request, "Please provide a rating.")
#             return redirect("skill_exchange:session_feedback_form", session_id=session_id)
        
#         try:
#             rating = float(rating)
#             if rating < 1 or rating > 5:
#                 raise ValueError("Rating must be between 1 and 5")
#         except (ValueError, TypeError):
#             messages.error(request, "Invalid rating. Must be between 1 and 5.")
#             return redirect("skill_exchange:session_feedback_form", session_id=session_id)
        
#         with transaction.atomic():
#             if existing_feedback:
#                 # Update existing feedback
#                 existing_feedback.rating = rating
#                 existing_feedback.comment = comment
#                 existing_feedback.status = SessionFeedbackStatus.SUBMITTED
#                 existing_feedback.save(update_fields=["rating", "comment", "status", "updated_at"])
#                 messages.success(request, "Feedback updated.")
#             else:
#                 # Create new feedback (anonymous)
#                 SessionFeedback.objects.create(
#                     exchange_session=session,
#                     rated_by_user=request.user,
#                     rated_user=other_user,
#                     rating=rating,
#                     comment=comment,
#                     status=SessionFeedbackStatus.SUBMITTED,
#                 )
#                 messages.success(request, "Feedback submitted anonymously.")
            
#             # Close the user's exchange post
#             with transaction.atomic():
#                 user_post.deleted_at = timezone.now()
#                 user_post.save(update_fields=["deleted_at"])
        
#         return redirect("skill_exchange:match_list")
    
#     context = {
#         "session": session,
#         "other_user": other_user,
#         "existing_feedback": existing_feedback,
#         "user_initiated_end": user_initiated_end,
#         "other_user_feedback_submitted": other_user_feedback is not None,
#     }
#     return render(request, "skill_exchange/session_feedback_form.html", context)


# @login_required
# def user_feedback_summary(request):
#     """Display all feedback received by the user (anonymous aggregation)"""
#     # Get all feedback received by the current user
#     feedback_list = SessionFeedback.objects.filter(
#         rated_user=request.user,
#         status=SessionFeedbackStatus.SUBMITTED,
#     ).select_related("exchange_session", "exchange_session__match").order_by("-given_at")
    
#     # Calculate statistics
#     total_feedback = feedback_list.count()
#     if total_feedback > 0:
#         average_rating = feedback_list.aggregate(models.Avg("rating"))["rating__avg"]
#     else:
#         average_rating = None
    
#     context = {
#         "feedback_list": feedback_list,
#         "total_feedback": total_feedback,
#         "average_rating": average_rating,
#     }
#     return render(request, "skill_exchange/user_feedback_summary.html", context)