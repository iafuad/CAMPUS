from django import forms
from django.contrib.auth import get_user_model
import re

User = get_user_model()


# ── UIU email parser ────────────────────────────────────────────────────────

UIU_DEPARTMENT_MAP = {
    #  email subdomain → (db short_code,  student ID prefix)
    "bscse":   ("CSE",   "011"),
    "mscse":   ("CSE",   "012"),
    "bsds":    ("DS",    "015"),
    "bseee":   ("EEE",   "021"),
    "bsce":    ("CE",    "031"),
    "bba":     ("BBA",   "111"),
    "mba":     ("MBA",   "112"),
    "bseco":   ("ECO",   "121"),
    "bae":     ("ENG",   "231"),
    "bssmsj":  ("SMSJ",  "221"),
    "bsseds":  ("SEDS",  "211"),
    "bsbge":   ("BGE",   "321"),
    "bpharm":  ("PHARM", "311"),
}

_LOCAL_RE = re.compile(r"^[a-zA-Z]+(\d{7,})$")


def parse_uiu_email(email: str) -> dict:
    email = email.strip().lower()

    if "@" not in email:
        raise ValueError("Enter a valid email address.")

    local, _, domain = email.partition("@")

    if not domain.endswith(".uiu.ac.bd"):
        raise ValueError("Only UIU institutional emails (@....uiu.ac.bd) are allowed.")

    dept_code = domain.removesuffix(".uiu.ac.bd")

    if not dept_code:
        raise ValueError("Invalid UIU email format.")

    if dept_code not in UIU_DEPARTMENT_MAP:
        raise ValueError(f"'{dept_code}' is not a recognised UIU department code.")

    db_short_code, id_prefix = UIU_DEPARTMENT_MAP[dept_code]

    match = _LOCAL_RE.match(local)
    if not match:
        raise ValueError("Invalid UIU email format.")

    digits     = match.group(1)       # e.g. "2420108"
    batch      = digits[:3]           # e.g. "242"
    student_id = f"{id_prefix}{digits}"  # e.g. "0112420108"

    return {
        "db_short_code": db_short_code,   # e.g. "CSE"  — matches Department.short_code
        "batch":         int(batch),      # e.g. 242    — matches Trimester.code
        "student_id":    student_id,
    }


# ── Registration form ───────────────────────────────────────────────────────

class RegisterForm(forms.ModelForm):
    password         = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model  = User
        fields = ["first_name", "last_name", "handle", "email", "password"]

    def clean_email(self):
        email = self.cleaned_data.get("email", "")
        try:
            self._uiu_info = parse_uiu_email(email)
        except ValueError as e:
            raise forms.ValidationError(str(e))
        return email.strip().lower()

    def clean(self):
        cleaned_data     = super().clean()
        password         = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            self._populate_profile(user)

        return user

    def _populate_profile(self, user):
        from apps.academics.models import Department, Trimester

        info    = self._uiu_info
        profile = user.profile  # created by your post_save signal

        profile.student_id = info["student_id"]

        # Matches Department.short_code e.g. "CSE", "EEE"
        profile.department = Department.objects.filter(
            short_code=info["db_short_code"]
        ).first()

        # Get trimester if it exists, otherwise create it from the batch code
        trimester, created = Trimester.objects.get_or_create(
            code=info["batch"]
        )
        profile.admission_trimester = trimester

        profile.save(update_fields=["student_id", "department", "admission_trimester"])