from django import forms
from django.contrib.auth.models import User


class QuestionForm(forms.Form):
    question_text = forms.CharField(
        label="Текст вопроса",
        max_length=200
    )
    choices_text = forms.CharField(
        label="Варианты ответа",
        widget=forms.Textarea
    )

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username",)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data