from django import forms
from apps.custom_auth.models import CustomUser


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'role', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.role == 'superadmin':
            self.fields['role'].disabled = True
            self.fields['role'].help_text = "Роль суперадмина нельзя изменить"

class PasswordForm(forms.Form):
    new_password = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput,
        required=True)

class UploadExcelForm(forms.Form):
    file = forms.FileField(
        label="Файл Excel",
        #help_text="Формат: .xlsx",
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx'})
    )