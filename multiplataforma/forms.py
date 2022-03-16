from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.db.models.fields import BLANK_CHOICE_DASH
from .models import Product, SubProduct, UserData, City, MoneysSaler, PlansPlatform


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name']


class SubProductForm(forms.ModelForm):
    instructions = forms.CharField(widget=forms.Textarea, label="Instrucciones")

    class Meta:
        model = SubProduct
        fields = ['name', 'price', 'instructions', 'renewable']


class SignUpForm(UserCreationForm):

    first_name = forms.CharField(max_length=30, required=True, help_text='Requerido.', label="Nombres")
    last_name = forms.CharField(max_length=30, required=True, help_text='Requerido.', label="Apellidos")
    email = forms.EmailField(max_length=254, help_text='Requerido. Digite un email válido..', label="Email")
    username = forms.CharField(max_length=254, help_text='Requerido. ', label="Username")
    password1 = forms.CharField(max_length=254, help_text='Contraseña', label="Contraseña", widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=254, help_text='Confirme la contraseña', label="Confirme la contraseña", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'first_name', 'is_active', 'last_name', 'email','password1', 'password2')


class AddMoneyForm(forms.ModelForm):
    class Meta:
        model = MoneysSaler
        fields = [ 'money']


class EditUserForm(UserCreationForm):

    first_name = forms.CharField(max_length=30, required=True, help_text='Requerido.', label="Nombres")
    last_name = forms.CharField(max_length=30, required=True, help_text='Requerido.', label="Apellidos")
    email = forms.EmailField(max_length=254, help_text='Requerido. Digite un email válido..', label="Email")

    class Meta:
        model = User
        fields = ('first_name', 'is_active', 'last_name', 'email')

    def save(self, commit=True):
        user = super(EditUserForm, self).save(commit=False)
        print('por aca')
        password = self.cleaned_data["password1"]
        if password:
            user.password = password
        if commit:
            user.save()
        return user

class UserDataForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(UserDataForm, self).__init__(*args, **kwargs)
        self.fields['city'] = forms.ModelChoiceField(queryset=City.objects.all(), widget=forms.Select(attrs={'placeholder': 'Ciudad'}))

    address = forms.CharField(required=True,max_length=254, help_text='Requerido. ', label="Dirección")
    phones = forms.CharField(required=True,max_length=254, help_text='Requerido', label="Telefonos")
    observations = forms.CharField(required=False, widget=forms.Textarea, label="Observaciones")

    class Meta:
        model = UserData
        fields = ('address', 'phones', 'city', 'observations')


class SubProductForm(forms.ModelForm):
    instructions = forms.CharField(widget=forms.Textarea, label="Instrucciones")

    class Meta:
        model = SubProduct
        fields = ['name', 'price', 'instructions', 'renewable']


class PlanProductForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PlanProductForm, self).__init__(*args, **kwargs)

        # self.fields['email']  = forms.EmailField(max_length=1000, help_text='Requerido. Digite un email válido..',label="Email")
        # self.fields['password'] = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = PlansPlatform
        fields = ['email', 'password', 'profile', 'pin']
