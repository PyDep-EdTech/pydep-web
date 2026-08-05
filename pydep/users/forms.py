from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput

from .models import CustomUser


class SignInForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя',
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя пользователя',
                'autofocus': True,
            }
        ),
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите пароль',
                'autocomplete': 'current-password',
            }
        ),
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'password')


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Иван'}
        ),
    )
    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Иванов'}
        ),
    )
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'ivan_dev'}
        ),
    )
    email = forms.EmailField(
        label='Почта',
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'ivan@example.com'}
        ),
    )
    image = forms.ImageField(
        label='Фотография профиля',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'img-upload__input', 'accept': 'image/*'}
        ),
    )
    password1 = forms.CharField(
        label='Пароль',
        strip=False,
        widget=PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Минимум 8 символов',
                'autocomplete': 'new-password',
            }
        ),
        help_text='Не менее 8 символов, не только цифры.',
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        strip=False,
        widget=PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Повторите пароль',
                'autocomplete': 'new-password',
            }
        ),
        help_text='Повторите пароль для проверки.',
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and CustomUser.objects.filter(
            username__iexact=username
        ).exists():
            raise forms.ValidationError(
                'Пользователь с таким именем уже существует.'
            )
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Этот email уже зарегистрирован.'
            )
        return email

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'image',
            'password1',
            'password2',
        )
