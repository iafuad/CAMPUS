from django.shortcuts import redirect, render, get_object_or_404

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from .models import Thread, ThreadMessage, MessageAttachment, ThreadParticipant
from apps.common.choices import ThreadStatus, ThreadParticipantRole
from apps.media.models import Photo


# threads/views.py
@login_required
def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    if not ThreadParticipant.objects.filter(thread=thread, user=request.user).exists():
        return HttpResponseForbidden("You are not a participant of this thread!")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        files = request.FILES.getlist("photos")

        if content:
            with transaction.atomic():
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

            return HttpResponseRedirect(
                reverse("threads:thread_detail", args=[thread.id])
            )

    context = {
        "thread": thread,
        "messages": thread.messages.select_related("sender")
        .prefetch_related("attachments__photo")
        .order_by("sent_at"),
        "claim_context": getattr(thread, "claim_thread", None),
    }

    return render(request, "threads/thread_detail.html", context)


@login_required
def archive_thread(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    if not ThreadParticipant.objects.filter(thread=thread, user=request.user).exists():
        return HttpResponseForbidden("You are not a participant of this thread!")
    user_role = ThreadParticipant.objects.get(thread=thread, user=request.user).role
    if user_role not in [ThreadParticipantRole.AUTHOR, ThreadParticipantRole.MODERATOR]:
        return HttpResponseForbidden("Only authors and moderators can archive threads!")

    if request.method == "POST":
        with transaction.atomic():
            thread.status = ThreadStatus.ARCHIVED
            thread.save(update_fields=["status", "updated_at"])
    return redirect("threads:thread_detail", thread_id=thread.id)
