from django import forms
from .models import LostAndFoundPost, ClaimRequest


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.ImageField):
    """A FileField that accepts and validates multiple uploaded files."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # No files submitted
        if not data:
            if self.required:
                raise forms.ValidationError(self.error_messages["required"])
            return []

        # Normalize to a list (could be a single InMemoryUploadedFile)
        if not isinstance(data, (list, tuple)):
            data = [data]

        # Run the parent FileField validation on each file individually
        return [super(MultipleFileField, self).clean(f, initial) for f in data]


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
        ]
        widgets = {
            "lost_or_found_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ClaimRequestForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Explain why you are claiming this item...",
            }
        ),
        label="Your Message",
    )
