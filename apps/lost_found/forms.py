from django import forms
from .models import lost_and_found_post, claim_request

class LostAndFoundPostForm(forms.ModelForm):
    uploaded_photos = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
        label="Upload Photos"
    )

    class Meta:
        model = lost_and_found_post
        fields = [
            'title',
            'description',
            'lost_or_found_date',
            'location',
            'type',
            'lost_and_found_category',
        ]
        widgets = {
            'lost_or_found_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'type': forms.Select(choices=[('lost', 'Lost'), ('found', 'Found')])
        }


class ClaimRequestForm(forms.ModelForm):
    class Meta:
        model = claim_request
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Explain why you are claiming this item or provide proof of ownership/finding...'
            }),
        }