from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from .models import Profile
from .domain_filter import EmailFilter
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

blob = EmailFilter()


def validate_censor_mail(value):
    if blob.check(value) is True:
        raise ValidationError(_('Please use email from another service provider.'))


def validate_unique_email(email):
    if User.objects.filter(email=email).exists():
        raise ValidationError(_("Email exists"))
    return email


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(validators=[validate_email, validate_censor_mail, validate_unique_email], help_text=_('Required unique Email'))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [_('image')]
