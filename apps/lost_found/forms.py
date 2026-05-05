from django import forms
from .models import LostAndFoundPost, ClaimRequest


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class LostAndFoundPostForm(forms.ModelForm):
    uploaded_photos = forms.ImageField(
        widget=MultipleFileInput(attrs={"multiple": True}),
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
        ]
        widgets = {
            "lost_or_found_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "type": forms.Select(choices=[("lost", "Lost"), ("found", "Found")]),
        }


class ClaimRequestForm(forms.ModelForm):
    class Meta:
        model = ClaimRequest
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Explain why you are claiming this item or provide proof of ownership/finding...",
                }
            ),
        }
