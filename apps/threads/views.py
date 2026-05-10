from django.shortcuts import render, get_object_or_404

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Thread, ThreadMessage, MessageAttachment
from apps.media.models import Photo


# threads/views.py
@login_required
def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)

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
