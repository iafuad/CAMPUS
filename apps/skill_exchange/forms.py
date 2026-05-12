from django import forms
from .models import ExchangePost, Skill

class SkillExchangePostForm(forms.ModelForm):
    class Meta:
        model = ExchangePost
        fields = ["description", "skills_offered", "skills_needed"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        offered_skills = cleaned_data.get("skills_offered")
        needed_skills = cleaned_data.get("skills_needed")

        if offered_skills and needed_skills:
            # Convert to sets of IDs for comparison
            offered_ids = set(s.id for s in offered_skills)
            needed_ids = set(s.id for s in needed_skills)
            overlap = offered_ids.intersection(needed_ids)
            if overlap:
                raise forms.ValidationError("You cannot offer a skill that you are also requesting.")
        
        return cleaned_data