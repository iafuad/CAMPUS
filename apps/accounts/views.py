import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import RegisterForm
from .models import UserProfile
from apps.skill_exchange.models import UserSkill, Skill
from apps.academics.models import Department


def profile_view(request, handle):
    profile = get_object_or_404(UserProfile, user__handle=handle)
    skills = UserSkill.objects.filter(user=profile.user).select_related("skill")
    is_own_profile = request.user.is_authenticated and request.user.handle == handle

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
            "skills": [us.skill for us in skills],
            "is_own_profile": is_own_profile,
            # Passed for the edit modal dropdowns
            "all_departments": Department.objects.all().order_by("name"),
            "all_skills": Skill.objects.all().order_by("name"),
            "user_skill_ids": list(skills.values_list("skill_id", flat=True)),
        },
    )


@login_required
@require_POST
def edit_profile(request, handle):
    # Only the profile owner can edit
    if request.user.handle != handle:
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid request body"}, status=400)

    user = request.user
    profile = get_object_or_404(UserProfile, user=user)

    # ── User fields ──────────────────────────────────────────────────────
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()

    if not first_name or not last_name:
        return JsonResponse(
            {"error": "First name and last name are required."}, status=400
        )

    user.first_name = first_name
    user.last_name = last_name
    user.save(update_fields=["first_name", "last_name"])

    # ── Profile fields ───────────────────────────────────────────────────
    profile.bio = data.get("bio", "").strip()
    profile.student_id = data.get("student_id", "").strip() or None

    dept_id = data.get("department_id")
    if dept_id:
        try:
            profile.department = Department.objects.get(id=dept_id)
        except Department.DoesNotExist:
            profile.department = None
    else:
        profile.department = None

    profile.save(update_fields=["bio", "student_id", "department"])

    # ── Skills ───────────────────────────────────────────────────────────
    skill_ids = data.get("skill_ids", [])
    valid_skills = Skill.objects.none()
    if isinstance(skill_ids, list) and skill_ids:
        UserSkill.objects.filter(user=user).delete()
        valid_skills = Skill.objects.filter(id__in=skill_ids)
        UserSkill.objects.bulk_create(
            [UserSkill(user=user, skill=skill) for skill in valid_skills]
        )
    elif isinstance(skill_ids, list):
        # Empty list means the user cleared all skills
        UserSkill.objects.filter(user=user).delete()

    # Build the response payload so the JS can update the page without a reload
    dept = profile.department
    return JsonResponse(
        {
            "success": True,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": profile.bio,
            "student_id": profile.student_id or "",
            "department_id": dept.id if dept else "",
            "department_name": f"{dept} ({dept.short_code})" if dept else "",
            "skills": [{"id": s.id, "name": s.name} for s in valid_skills],
        }
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
