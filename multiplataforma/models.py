from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Avg, Count, Min, Sum
from .validators import valid_extension, valid_image_extension
import pytz
from django.forms import model_to_dict
import datetime
from django.db.models import OuterRef, Exists

def dates_init_finish(year, month):
    import calendar
    lastday = calendar.monthrange(year, int(month))[1]
    initial_date = datetime.datetime.strptime(str(year) + "-" + str(month) + "-01", '%Y-%m-%d')
    initial_date = initial_date - datetime.timedelta(hours=5)
    final_date = datetime.datetime.strptime(str(year) + "-" + str(month) + "-" + str(lastday), '%Y-%m-%d')
    final_date = final_date + datetime.timedelta(hours=19)
    return [initial_date, final_date]


class ActionUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=300, default="")
    date = models.DateTimeField(auto_now_add=True)


class Country(models.Model):

    country = models.CharField(default="", max_length=100, verbose_name="Pais")
    iso =  models.CharField(default="", max_length=3, verbose_name="Iso")

    def __str__(self):
        return self.country


class UserData(models.Model):

    user= models.ForeignKey(User, on_delete=models.CASCADE)
    #document  = models.CharField(max_length=15, verbose_name="Documento", default="")
    image_document = models.FileField(default="", upload_to='documents', validators=[valid_extension])
    address = models.CharField(max_length=150, verbose_name="Dirección", default="")
    phones = models.CharField(max_length=150, verbose_name="Dirección", default="")
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    state = models.CharField(max_length=50, verbose_name="Estado", default="")
    city = models.CharField(max_length=50, verbose_name="Ciudad", default="")
    observations = models.CharField(default="", max_length=255, verbose_name="Observaciones")
    image = models.ImageField(upload_to='photos', validators=[valid_extension])
    #bank_info = models.CharField(max_length=300, verbose_name="Información Bancaria", default="")
    paypal = models.CharField(blank=True, null=True, max_length=100, verbose_name="PayPal", default="")
    aritms = models.CharField(blank=True, null=True, max_length=100, verbose_name="Aritms", default="")
    binance = models.CharField(blank=True, null=True, max_length=100, verbose_name="Binance", default="")
    banco = models.CharField(blank=True, null=True, max_length=150, verbose_name="Banco", default="")
    token_register = models.CharField(max_length=150, verbose_name="Token", default="")
    email_verified = models.BooleanField(default=0, verbose_name="Email verificado?:")


class Product(models.Model):

    name = models.CharField(max_length=150, verbose_name="Nombre", default="")
    active = models.BooleanField(default=1, verbose_name="Activo?:")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)

    @classmethod
    def get_all_products(self):

        products = self.objects.filter(active=1)
        return products

class PercentCommission(models.Model):

    percent = models.FloatField(verbose_name="Porcentaje" )
    date = models.DateTimeField(auto_now_add=True)


class ImagesCarrousel(models.Model):

    image = models.FileField(default="", upload_to='carrousel', validators=[valid_image_extension])
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_carrousel_images(cls):

        images = cls.objects.all().order_by('-date')[0:3]
        return images


class SubProduct(models.Model):

    product = models.ForeignKey(Product, default=1, verbose_name="Plataforma", on_delete=models.CASCADE)
    name = models.CharField(max_length=150, verbose_name="Nombre", default="")
    price = models.IntegerField(default=0, verbose_name="Precio general", )
    renewable = models.BooleanField(default=0, verbose_name="Renovable?")
    instructions = models.CharField(max_length=1000, verbose_name="Instrucciones", default="")
    active = models.BooleanField(default=1, verbose_name="Activo?")
    date = models.DateTimeField(auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creater") #usuario creador
    #owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")#usuario dueño actual
    for_sale = models.BooleanField(default=False, verbose_name="para la venta?")
    individual_sale = models.BooleanField(default=False, verbose_name="Venta por cuenta")

    def __str__(self):
        return str(self.name)



class CountsPackage(models.Model):

    subproduct = models.ForeignKey(SubProduct, default=1, verbose_name="Producto", on_delete=models.CASCADE)
    email = models.CharField(max_length=100, verbose_name="Email")
    password = models.CharField(max_length=50, default="")
    profile = models.CharField(blank=True, max_length=20, verbose_name="Perfil", default="")
    pin = models.CharField(max_length=4, verbose_name="Pin", default="0")
    saled =  models.BooleanField(default=0, verbose_name="Vendida?")
    price_buy = models.IntegerField(default=0, verbose_name="Precio de Compra")
    date_buy = models.DateTimeField(auto_now_add=False, null=True)
    #price_sale = models.IntegerField(default=0, verbose_name="Precio de venta" )
    date_sale  = models.DateTimeField(auto_now_add=False,  null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # usuario dueño actual
    pay_value = models.IntegerField(default=0, verbose_name="Comision")
    commission = models.IntegerField(default=0, verbose_name="Comision")
    commission_payed = models.BooleanField(default=False, verbose_name="Comision pagada?")
    commission_collect = models.BooleanField(default=False, verbose_name="Comision cobrada?")
    #commission_collect_payment = models.CharField(default="", max_length=10, verbose_name="Método de pago")
    date_pay = models.DateTimeField(blank=True, null=True, auto_now_add=False)
    date_finish = models.DateTimeField(auto_now_add=False, null=True)
    request_renewal = models.BooleanField(default=False, verbose_name="Solicitar renovación")
    months_renew = models.IntegerField(default=0, verbose_name="Meses")

    def __str__(self):
        return str(self.email)

    @classmethod
    def RenewPending(cls, user):

        request_renewal = cls.objects.filter(subproduct__creater=user, request_renewal=True)
        return request_renewal
    @classmethod
    def SalesPendingCommission(cls, user):

        sales = cls.objects.filter(subproduct__creater=user, commission_payed=False, commission_collect=False).filter(~Q(owner=user))
        return sales

    @classmethod
    def SalesPendingPayCommission(cls, user):

        sales = cls.objects.filter(subproduct__creater=user, commission_payed=False,
                                             commission_collect=True)
        return sales

    @classmethod
    def AllSalesPendingCommission(cls):

        sales = cls.objects.filter(commission_payed=False, commission_collect=True)
        return sales

    @classmethod
    def SalesPendingCommissionByPayment(cls, user, payment):

        sales = cls.objects.filter(subproduct__creater=user, commission_payed=False, commission_collect=True, commission_collect_payment=payment )
        return sales


    @classmethod
    def SalesByStaffbyDate(cls, user, year, month):

        initial_date, final_date = dates_init_finish(year, month)
        subproducts = SubProduct.objects.filter(creater=user)
        my_counts_sales = cls.objects.filter(subproduct__in=subproducts).filter(~Q(owner=user)).filter(date_buy__range=[initial_date, final_date])
        return my_counts_sales

    @classmethod
    def get_all_counts_package_no_sales(cls, subproduct):

        CountsPackage = cls.objects.filter(subproduct=subproduct, owner=subproduct.creater)
        return CountsPackage

    @classmethod
    def get_mys_counts_package_no_sales(cls, subproduct, me):

        CountsPackage = cls.objects.filter(subproduct=subproduct, owner=me,saled=False)
        return CountsPackage


    def sale_count(cls, months):

        days =  int(months) * 30
        date_finish = cls.date_finish + datetime.timedelta(days=days)
        cls.date_finish = date_finish
        cls.saled = True
        cls.date_sale = datetime.datetime.now()
        cls.save()


    def resale_count(self,  months):

        now = datetime.datetime.now()
        utc = pytz.UTC
        now = now.replace(tzinfo=utc)
        days = int(months) * 30
        if  now > self.date_finish.replace(tzinfo=utc) :
            initial_date = self.date_finish + datetime.timedelta(days=1)
            date_finish =  initial_date + datetime.timedelta(days=days)
            kwargs = model_to_dict(self, exclude=['id'])
            kwargs['subproduct'] = SubProduct.objects.filter(id= kwargs['subproduct']).first()
            kwargs['owner'] = User.objects.filter(id=kwargs['owner']).first()
            kwargs['date_buy'] = datetime.datetime.now()
            kwargs['date_finish'] = date_finish
            kwargs['request_renewal'] = 0
            kwargs['months_renew'] = 0
            CountsPackage.objects.create(**kwargs)

    @classmethod
    def sales_to_expire(cls, user, days):

        if days == 0:
            date = datetime.date.today()
        else:
            date = datetime.date.today() + datetime.timedelta(days=days)
        sales_to_expire = cls.objects.filter(owner = user).filter(date_finish__range=[datetime.date.today(), date ]).order_by('-date_finish')
        return sales_to_expire

    @classmethod
    def all_counts_buy_in_dates(cls, user, year, month):

        initial_date, final_date = dates_init_finish(year, month)
        sales = cls.objects.filter(owner=user).filter(date_buy__range=[initial_date, final_date]).order_by('-date_buy')
        return sales


    @classmethod
    def all_counts_saled_in_dates(cls, year, month, request):

        initial_date, final_date = dates_init_finish(year, month)
        sales = cls.objects.filter(owner=request.user, saled=1).filter(date_sale__range=[initial_date, final_date])
        return sales


    @classmethod
    def all_counts_saled_for_date(cls, date):

        sales = cls.objects.filter(saled=1).filter(date_sale__startswith=date)
        return sales

    @classmethod
    def staff_all_counts_saled_for_date(cls, date):

        subproduct = SubProduct.objects.filter(creater=user)
        counts_package = cls.objects.filter(subproduct__in=subproduct)
        reports = cls.objects.filter(state=0,  count__in=counts_package).order_by('-date')
        return reports

        #sales = cls.objects.filter(saled=1).filter(date_sale__startswith=date)
        #return sales

    def SetPayStaffSale(cls):

        percent = PercentCommission.objects.all().first().percent
        commission = cls.price_buy * (percent * 0.01)
        pay = cls.price_buy-commission
        cls.pay_value = pay
        cls.commission_payed = 1
        cls.date_pay = datetime.datetime.now()
        cls.save()
        return cls

    @classmethod
    def SalesAllbyDate(self, year, month):

        initial_date, final_date = dates_init_finish(year, month)
        sales = self.objects.filter(commission_payed=True).filter(date_pay__range=[initial_date, final_date])
        return sales


class Invoice(models.Model):

    date_create = models.DateTimeField(auto_now_add=True)
    payed = models.BooleanField(default=0, verbose_name="Pagada?:")
    date_pay = models.DateTimeField(blank=True, null=True, auto_now_add=False)
    due = models.ForeignKey(User, on_delete=models.CASCADE) #Usuario adeudante
    payment_method = models.CharField(default="", max_length=10, verbose_name="Método de pago")

    def __str__(self):
        return str(self.id)

    @classmethod
    def UserPendingInvoices(cls):

        users = []
        invoices = cls.objects.filter(payed=False).values('due').annotate(count=Count('id')).order_by()
        for invoice in invoices:
            user = User.objects.filter(id=invoice['due'], is_superuser=False).last()
            if user:
                users.append(user)

        return users

class CountPackageInvoice(models.Model):

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    count_package = models.ForeignKey(CountsPackage, on_delete=models.CASCADE)

    @classmethod
    def UserPendingInvoices(cls):

        invoices = Invoice.objects.filter(payed=False)
        counts_package = cls.objects.filter(invoice__in=invoices)
        counts_package = counts_package.annotate(is_duplicate=Exists(
            cls.objects.filter(
                count_package__lt=OuterRef('count_package')
                )))
        counts_package = counts_package.filter(is_duplicate=False)
        return counts_package


#class CountPackageSale(models.Model):

#   saler = models.ForeignKey(User, on_delete=models.CASCADE)#
#    counts_package = models.ForeignKey(CountsPackage, on_delete=models.CASCADE, default="")
#    price = models.IntegerField(default=0)
#    is_renovation = models.BooleanField(default=0, verbose_name="Es renovacion?:")
#    date = models.DateTimeField(auto_now_add=True)


class UserProduct(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saler")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="staff")



class MoneysSaler(models.Model):

    saler = models.ForeignKey(User, verbose_name="Usuario", on_delete=models.CASCADE)
    detail = models.CharField(default="", verbose_name="Detalle", max_length=150)
    transaction_money = models.IntegerField(default=0, verbose_name="Comision")
    money = models.IntegerField(default=0, verbose_name="Dinero a agregar")
    date = models.DateTimeField(auto_now_add=True, null=True)



    @classmethod
    def Get_mys_money_saler(self):

        money_saler = self.objects.all().order_by('-date')
        return money_saler

    @classmethod
    def Get_mys_transactions(self,  user,  year, month):

        initial_date, final_date = dates_init_finish(year, month)
        trasnsactions = self.objects.filter(saler = user).filter(date__range=[initial_date, final_date])
        return trasnsactions

    def __str__(self):
        return str(self.money)



class IssuesReport(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.ForeignKey(CountsPackage, on_delete=models.CASCADE)
    state = models.BooleanField(default=0, verbose_name="Resuelto?:")
    issue = models.CharField(max_length=1000, verbose_name="Problema", default="")
    image = models.FileField(blank=True, null=True, upload_to='errors', validators=[valid_extension])
    date = models.DateTimeField(auto_now_add=True)
    response = models.CharField(max_length=1000, verbose_name="Respuesta", default="")


    @classmethod
    def get_reports_of_mys_counts_created(self, user):

        subproduct = SubProduct.objects.filter(creater=user)
        counts_package = CountsPackage.objects.filter(subproduct__in=subproduct)
        reports = self.objects.filter(state=0,  count__in=counts_package).order_by('-date')
        return reports

    @classmethod
    def get_mys_reports_pendding(self, user):

        reports = self.objects.filter(state=0, user=user).order_by('-date')
        return reports

    @classmethod
    def get_mys_reports_solucionated(self, user):
        reports = self.objects.filter(state=1, user=user).order_by('-date')
        return reports

    @classmethod
    def get_reports_pendding(self):

        reports = self.objects.filter(state=0 ).order_by('-date')
        return reports


class UserStart(models.Model):

    saler = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_saler")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_buyer")
    stars = models.IntegerField(default=0, verbose_name="Estrellas")
    date = models.DateTimeField(auto_now_add=True)

#**************************funciones para user adicionales********************************************


def get_stars_saler(cls, buyer):

    saler_stars = UserStart.objects.filter(saler=cls,buyer=buyer).first()
    stars = 0
    if saler_stars:
        stars = saler_stars.stars
    return stars


def get_general_stars_saler(cls):

    starts = 0
    saler_stars = UserStart.objects.filter(saler=cls).aggregate(Avg('stars'))
    if saler_stars['stars__avg']:
        starts = int(saler_stars['stars__avg'])
    return starts

def get_mys_products_actives(cls):

    products_actives = UserProduct.objects.filter(user=cls).filter(product__active = True)
    return products_actives

#trae subproductos comprados por el vendedor
def get_my_buy_subproducts_actives_by_product(cls, product):

    mys_subproducts =  list(CountsPackage.objects.filter(owner=cls, saled=False).values_list('subproduct_id', flat=True))

    my_sub_products_actives = SubProduct.objects.filter(product=product, active=True, id__in=mys_subproducts)
    return my_sub_products_actives

def subtract_money(cls, money_user, money_to_discount, detail):

    money_to_discount = int(money_to_discount)
    if money_user >= money_to_discount:
        remains = money_user - money_to_discount
        if remains >= 0:
            MoneysSaler.objects.create(money=remains, saler=cls, detail=detail,
                                      transaction_money=money_to_discount)
            return remains
    return False

def add_money_user(cls, money_saler, transaction_money, detail):

    money = int(money_saler)
    transaction_money = int(transaction_money)
    if transaction_money > 0:
        remains = money + transaction_money
        MoneysSaler.objects.create(money=remains, saler_id=cls.id, detail=detail,  transaction_money=transaction_money)
        return remains


def get_my_money(cls):

    money_saler = MoneysSaler.objects.filter(saler=cls).last()
    if money_saler:
        return money_saler.money
    else:
        return 0

def get_my_salers(cls):

    my_counts = list(CountsPackage.objects.filter(owner = cls).values_list('subproduct_id', flat=True))
    unique_list = list(dict.fromkeys(my_counts))
    subrpoducts = list(SubProduct.objects.filter(id__in=unique_list).values_list('creater_id', flat=True))
    my_salers = User.objects.filter(is_active=True, id__in= subrpoducts)
    return my_salers

def get_my_general_sales(cls):

    subproducts =SubProduct.objects.filter(creater=cls)
    my_counts_sales = CountsPackage.objects.filter( subproduct__in=subproducts).filter(~Q(owner=cls))
    return my_counts_sales

def get_mys_invoices_pendding(self):

    invoices = Invoice.objects.filter(payed=False, due=self )
    return invoices

def get_mys_invoices_payed(self):

    invoices = Invoice.objects.filter(payed=True, due=self )
    return invoices


User.add_to_class("get_mys_invoices_payed",get_mys_invoices_payed)
User.add_to_class("get_mys_invoices_pendding",get_mys_invoices_pendding)
User.add_to_class("get_general_stars_saler",get_general_stars_saler)
User.add_to_class("get_stars_saler",get_stars_saler)
User.add_to_class("get_my_salers",get_my_salers)
User.add_to_class("get_mys_products_actives",get_mys_products_actives)
User.add_to_class("add_money_user",add_money_user)
User.add_to_class("get_my_money",get_my_money)
User.add_to_class("subtract_money",subtract_money)
User.add_to_class("get_my_general_sales",get_my_general_sales)
User.add_to_class("get_my_buy_subproducts_actives_by_product",get_my_buy_subproducts_actives_by_product)
#**************************fin funciones para user adicionales********************************************
#class PlanPriceBySaler(models.Model):

#    saler = models.ForeignKey(User, default=1, verbose_name="Vendedor", on_delete=models.CASCADE)
#    plan = models.ForeignKey(Plan, default=1, verbose_name="Plan", on_delete=models.CASCADE)
#    price = models.IntegerField(default=0)

#    def __str__(self):
#        return str(self.plan) + "  $" + str(self.price)

#    @classmethod
#    def get_my_plans(self, user_id):
#        plans = self.objects.filter(saler_id=user_id).select_related('plan')
#        return plans
