from django import forms


class RegisterForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control my-2', 'placeholder': 'email@domen.ru'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2'}))
    password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2'}))