from django import forms
from .models import LostAndFoundPost, ClaimRequest
from apps.common.choices import LostAndFoundPostType, LostAndFoundStatus

# ---------------------------------------------------------------------------
# Shared widget / field helpers
# ---------------------------------------------------------------------------


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.ImageField):
    """ImageField that accepts and validates multiple uploaded files."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            if self.required:
                raise forms.ValidationError(self.error_messages["required"])
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        return [super(MultipleFileField, self).clean(f, initial) for f in data]


# ---------------------------------------------------------------------------
# Post form
# ---------------------------------------------------------------------------


class LostAndFoundPostForm(forms.ModelForm):
    uploaded_photos = MultipleFileField(
        required=False,
        label="Upload Photos",
    )

    class Meta:
        model = LostAndFoundPost
        fields = [
            "title",
            "description",
            "lost_or_found_date",
            "location",
            "type",
            "category",
            "tags",
        ]
        widgets = {
            "lost_or_found_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "tags": forms.CheckboxSelectMultiple(),
        }


# ---------------------------------------------------------------------------
# Claim form
# ---------------------------------------------------------------------------


class ClaimRequestForm(forms.ModelForm):
    """
    Form for submitting a claim against a found post.

    Requires `user` and `found_post` kwargs so it can:
      - restrict `lost_post` to only the claimer's own active lost posts
      - exclude the found_post's category mismatch (nice to have, not enforced)

    Usage in view:
        form = ClaimRequestForm(request.POST, user=request.user, found_post=post)
    """

    class Meta:
        model = ClaimRequest
        fields = ["lost_post", "message"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Describe your item in detail — colour, brand, any unique "
                        "markings — so the finder can verify your claim."
                    ),
                }
            ),
        }
        labels = {
            "lost_post": "Link your lost-item post (optional but recommended)",
            "message": "Your message to the finder",
        }
        help_texts = {
            "lost_post": (
                "Selecting your own lost-item report helps the finder verify "
                "your claim and may speed up resolution."
            ),
        }

    def __init__(self, *args, user=None, found_post=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["lost_post"].required = False
        self.fields["lost_post"].empty_label = (
            "— I don't have a corresponding lost post —"
        )

        if user is not None:
            # Only show the claimer's own active LOST posts
            self.fields["lost_post"].queryset = LostAndFoundPost.objects.filter(
                user=user,
                type=LostAndFoundPostType.LOST,
                status=LostAndFoundStatus.APPROVED,
                deleted_at__isnull=True,
            ).order_by("-created_at")
        else:
            self.fields["lost_post"].queryset = LostAndFoundPost.objects.none()
