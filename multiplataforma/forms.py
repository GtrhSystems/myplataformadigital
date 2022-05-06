from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.db.models.fields import BLANK_CHOICE_DASH
from .models import Product, SubProduct, UserData, Country, MoneysSaler, CountsPackage, IssuesReport


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name']



class SignUpForm(UserCreationForm):

    first_name = forms.CharField(max_length=30, required=True, help_text='Requerido.', label="Nombres")
    last_name = forms.CharField(max_length=30, required=True, help_text='Requerido.', label="Apellidos")
    email = forms.EmailField(max_length=254, help_text='Requerido. Digite un email válido..', label="Email")
    username = forms.CharField(max_length=254, help_text='Requerido. ', label="Username")
    password1 = forms.CharField(max_length=254, help_text='Contraseña', label="Contraseña", widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=254, help_text='Confirme la contraseña', label="Confirme la contraseña", widget=forms.PasswordInput())
    group = forms.ChoiceField(choices = (('staff', 'Proveedor'), ('vendedor','Distribuidor')))


    class Meta:
        model = User
        fields = ('username', 'first_name', 'is_active', 'last_name', 'email','password1', 'password2','group')


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
        self.fields['country'] = forms.ModelChoiceField(queryset=Country.objects.all(), widget=forms.Select(attrs={'placeholder': 'Pais'}))

    address = forms.CharField(required=True,max_length=254, help_text='Requerido. ', label="Dirección")
    phones = forms.CharField(required=True,max_length=254, help_text='Requerido', label="Telefonos", widget=forms.TextInput(attrs={'placeholder': 'ejemplo +52 33 333 33'}))
    #bank_info = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":3, "cols":10}), label="Información Bancaria")
    observations = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows":3, "cols":10}), label="Observaciones")

    class Meta:
        model = UserData
        fields = ('address', 'document', 'phones', 'state', 'city','country', 'observations', 'image','image_document', 'paypal', 'aritms','binance','banco')



class SubProductForm(forms.ModelForm):
    instructions = forms.CharField(widget=forms.Textarea, label="Instrucciones")
    individual_sale =  forms.ChoiceField(choices = (('',''),( '0', 'Paquete Completo'), ('1','Venta por cuentas')), widget=forms.Select(attrs={'placeholder': 'Tipo de venta'}))

    class Meta:
        model = SubProduct
        fields = ['name', 'price', 'instructions', 'individual_sale']


class PlanProductForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PlanProductForm, self).__init__(*args, **kwargs)

        # self.fields['email']  = forms.EmailField(max_length=1000, help_text='Requerido. Digite un email válido..',label="Email")
        # self.fields['password'] = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = CountsPackage
        fields = ['email', 'password', 'profile', 'pin']


class ReportIssueForm(forms.ModelForm):
    issue = forms.CharField(widget=forms.Textarea, label="Detalle")

    class Meta:
        model = IssuesReport
        fields = ['issue']


class ReportForm(forms.ModelForm):
    response = forms.CharField(widget=forms.Textarea, label="Detalle")

    class Meta:
        model = IssuesReport
        fields = ['state', 'response']


class GetInterDatesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        import datetime
        YEARS = [x for x in range(2022, 2040)]
        super(GetInterDatesForm, self).__init__(*args, **kwargs)
        date =datetime.date.today().strftime('%Y-%m-%d')
        self.fields['month_year'] = forms.DateField(label='Selceccion el mes de consulta', initial=date, widget=forms.SelectDateWidget(years=YEARS))

    class Meta:
        fields = ('month_year')