from django import forms


class RegisterForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control my-2', 'placeholder': 'email@domen.ru'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2'}))
    password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2'}))


class LoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя (*как в Telegram)', widget=forms.TextInput(attrs={'class':'form-control my-2'}))
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class':'form-control my-2'}),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)
