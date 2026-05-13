from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.academics.models import Trimester, Department, Course
from apps.common.choices import ThreadVisibility, VoteType
from apps.forum.forms import ForumThreadCreateForm, ThreadMessageForm
from apps.forum.models import ForumThread
from apps.threads.models import MessageVote, ThreadMessage


def get_current_trimester():
    """Helper to fetch the current active trimester."""
    return Trimester.objects.order_by("-code").first()


@login_required
def forum_index(request):
    """List and filter forum threads with active filter context."""
    threads = (
        ForumThread.objects.select_related(
            "thread", "author", "course", "department", "trimester"
        )
        .filter(
            Q(thread__visibility=ThreadVisibility.PUBLIC)
            | Q(thread__participants__user=request.user)
        )
        .distinct()
        .order_by("-thread__created_at")
    )

    dept_id = request.GET.get("department")
    course_query = request.GET.get("course")

    active_filters = []

    if dept_id and dept_id.isdigit():
        threads = threads.filter(department_id=dept_id)
        dept_obj = Department.objects.filter(id=dept_id).first()
        if dept_obj:
            active_filters.append(
                {"type": "dept", "id": dept_id, "label": dept_obj.short_code}
            )

    if course_query:
        threads = threads.filter(course__code__icontains=course_query)
        active_filters.append(
            {"type": "course", "val": course_query, "label": course_query}
        )

    context = {
        "threads": threads,
        "active_filters": active_filters,
    }
    return render(request, "forum/index.html", context)


@login_required
def search_suggestions(request):
    """API endpoint for fuzzy searching departments and courses."""
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse({"departments": [], "courses": []})

    # Fuzzy match on short_code or name
    depts = Department.objects.filter(
        Q(short_code__icontains=q) | Q(name__icontains=q)
    ).distinct()[:5]

    # Fuzzy match on course code or name
    courses = Course.objects.filter(
        Q(code__icontains=q) | Q(name__icontains=q)
    ).distinct()[:5]

    return JsonResponse(
        {
            "departments": [
                {"id": d.id, "label": f"{d.short_code}: {d.name}", "code": d.short_code}
                for d in depts
            ],
            "courses": [
                {"id": c.id, "label": f"{c.code}: {c.name}", "code": c.code}
                for c in courses
            ],
        }
    )


@login_required
def thread_create(request):
    """Create a new forum thread."""
    current_trimester = get_current_trimester()

    if request.method == "POST":
        form = ForumThreadCreateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            forum_thread = form.save(current_trimester=current_trimester)
            return redirect("forum:thread_detail", pk=forum_thread.pk)
    else:
        form = ForumThreadCreateForm(user=request.user)

    context = {"form": form}
    return render(request, "forum/thread_create.html", context)


@login_required
def thread_detail(request, pk):
    """Display a thread, its nested messages, and handle new replies."""
    forum_thread = get_object_or_404(
        ForumThread.objects.select_related(
            "thread", "author", "course", "department", "trimester"
        ),
        pk=pk,
    )
    base_thread = forum_thread.thread

    # Enforce private thread authorization
    if base_thread.visibility == ThreadVisibility.PRIVATE:
        is_participant = base_thread.participants.filter(user=request.user).exists()
        if not is_participant and forum_thread.author != request.user:
            raise Http404("You do not have permission to view this thread.")

    # Process new reply submission
    if request.method == "POST":
        form = ThreadMessageForm(request.POST, request.FILES)
        if form.is_valid():
            reply_to_id = request.POST.get("reply_to")
            reply_to = None
            if reply_to_id:
                reply_to = get_object_or_404(
                    ThreadMessage, pk=reply_to_id, thread=base_thread
                )

            form.save(thread=base_thread, sender=request.user, reply_to=reply_to)
            return redirect("forum:thread_detail", pk=pk)
    else:
        form = ThreadMessageForm()

    # 1. Base queryset for messages
    messages_qs = base_thread.messages.select_related(
        "sender", "reply_to"
    ).prefetch_related("attachments__photo")

    # 2. Identify the Pinned/Accepted Answer
    # We fetch this to display it in a special "Hero" slot at the top of the page.
    pinned_answer = messages_qs.filter(is_pinned=True).first()

    # 3. Get sort parameter from URL
    sort_option = request.GET.get("sort", "oldest")

    if sort_option == "top":
        messages = messages_qs.annotate(
            db_net_score=F("upvote_count") - F("downvote_count")
        ).order_by("-db_net_score", "sent_at")
    elif sort_option == "latest":
        messages = messages_qs.order_by("-sent_at")
    else:  # "oldest"
        messages = messages_qs.order_by("sent_at")

    # 4. Build Reddit-style nested tree hierarchy
    message_dict = {}
    root_messages = []

    # First pass: load all instances into dictionary
    for msg in messages:
        msg.replies_list = []
        message_dict[msg.id] = msg

    # Second pass: group into parents/roots
    for msg in messages:
        if msg.reply_to_id and msg.reply_to_id in message_dict:
            message_dict[msg.reply_to_id].replies_list.append(msg)
        else:
            root_messages.append(msg)

    context = {
        "forum_thread": forum_thread,
        "base_thread": base_thread,
        "root_messages": root_messages,
        "pinned_answer": pinned_answer,
        "form": form,
        "current_sort": sort_option,
    }
    return render(request, "forum/thread_detail.html", context)


@login_required
@require_POST
def toggle_message_pin(request, message_id):
    # 1. Fetch message and the associated ForumThread
    message = get_object_or_404(ThreadMessage, pk=message_id)
    try:
        forum_thread = message.thread.forumthread
    except ForumThread.DoesNotExist:
        return JsonResponse({"error": "Forum thread not found"}, status=404)

    # 2. Permission Check: Only the thread author can pin
    if forum_thread.author != request.user:
        return JsonResponse({"error": "Only the author can mark an answer"}, status=403)

    with transaction.atomic():
        if message.is_pinned:
            # Unpin current
            message.is_pinned = False
            message.save()
            action = "unpinned"
        else:
            # 3. Enforce Exclusivity: Unpin all other messages in this thread
            ThreadMessage.objects.filter(thread=message.thread, is_pinned=True).update(
                is_pinned=False
            )

            # Pin the new one
            message.is_pinned = True
            message.save()
            action = "pinned"

    return JsonResponse({"status": "success", "action": action})


@require_POST
@login_required
def vote_message(request, message_id):
    """Handle upvoting and downvoting on a message."""
    message = get_object_or_404(ThreadMessage, pk=message_id)
    vote_type_param = request.POST.get("vote_type")  # 'upvote' or 'downvote'

    if vote_type_param not in ["upvote", "downvote"]:
        return JsonResponse({"error": "Invalid vote type."}, status=400)

    target_vote_type = (
        VoteType.UPVOTE if vote_type_param == "upvote" else VoteType.DOWNVOTE
    )

    with transaction.atomic():
        # Lock the message row to prevent race conditions updating counts
        message = ThreadMessage.objects.select_for_update().get(pk=message_id)
        vote, created = MessageVote.objects.get_or_create(
            message=message,
            user=request.user,
            defaults={"vote_type": target_vote_type},
        )

        if not created:
            if vote.vote_type == target_vote_type:
                # Clicking the same vote twice revokes it
                vote.delete()
            else:
                # Switching vote type
                vote.vote_type = target_vote_type
                vote.save()

        # Recalculate accurate counts dynamically
        upvotes = message.votes.filter(vote_type=VoteType.UPVOTE).count()
        downvotes = message.votes.filter(vote_type=VoteType.DOWNVOTE).count()

        message.upvote_count = upvotes
        message.downvote_count = downvotes
        message.save(update_fields=["upvote_count", "downvote_count"])

    return JsonResponse(
        {
            "upvote_count": upvotes,
            "downvote_count": downvotes,
        }
    )
