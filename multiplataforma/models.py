from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
# Create your models here.




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
    address = models.CharField(max_length=150, verbose_name="Dirección", default="")
    phones = models.CharField(max_length=150, verbose_name="Dirección", default="")
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    observations = models.CharField(default="", max_length=255, verbose_name="Observaciones")
    image = models.ImageField(upload_to='photos')



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

class SubProduct(models.Model):

    product = models.ForeignKey(Product, default=1, verbose_name="Plataforma", on_delete=models.CASCADE)
    name = models.CharField(max_length=150, verbose_name="Nombre", default="")
    price = models.IntegerField(default=0, verbose_name="Precio general", )
    #renewable = models.BooleanField(default=0, verbose_name="Renovable?:")
    instructions = models.CharField(max_length=1000, verbose_name="Instrucciones", default="")
    active = models.BooleanField(default=1, verbose_name="Activo?")
    date = models.DateTimeField(auto_now_add=True)
    creater = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creater") #usuario creador
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")#usuario dueño actual
    for_sale = models.BooleanField(default=False, verbose_name="para la venta?:")

    def __str__(self):
        return str(self.name)




class CountsPackage(models.Model):

    subproduct = models.ForeignKey(SubProduct, default=1, verbose_name="Producto", on_delete=models.CASCADE)
    email = models.CharField(max_length=100, verbose_name="Email")
    password = models.CharField(max_length=50, default="")
    profile = models.CharField(max_length=20, verbose_name="Perfil", default="")
    pin = models.CharField(max_length=4, verbose_name="Pin", default="0")
    saled =  models.BooleanField(default=0, verbose_name="Vendida?")
    price_sale = models.IntegerField(default=0, verbose_name="Precio de venta" )

    def __str__(self):
        return str(self.email)

    @classmethod
    def get_all_counts_package_no_sales(self, subproduct):

        CountsPackage = self.objects.filter(subproduct=subproduct, saled=False)

        return CountsPackage

    def sale_count(cls, price):

        cls.saled = True
        cls.price_sale = int(price)
        cls.save()

class CountPackageSale(models.Model):

    saler = models.ForeignKey(User, on_delete=models.CASCADE)
    counts_package = models.ForeignKey(CountsPackage, on_delete=models.CASCADE, default="")
    price = models.IntegerField(default=0)
    is_renovation = models.BooleanField(default=0, verbose_name="Es renovacion?:")
    date = models.DateTimeField(auto_now_add=True)


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

    def __str__(self):
        return str(self.money)



class IssuesReport(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=100, verbose_name="Correo")
    platform = models.CharField(max_length=30, default="")
    state = models.BooleanField(default=0, verbose_name="Resuelto?:")
    issue = models.CharField(max_length=1000, verbose_name="Problema", default="")
    date = models.DateTimeField(auto_now_add=True)
    response = models.CharField(max_length=1000, verbose_name="Respuesta", default="")



class UserStart(models.Model):

    saler = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_saler")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_buyer")
    stars = models.IntegerField(default=0, verbose_name="Estrellas")
    date = models.DateTimeField(auto_now_add=True)

#**************************funciones para user adicionales********************************************


def get_stars_saler(cls, buyer):

    saler_stars = UserStart.objects.filter(saler=cls,buyer=buyer).first()
    return saler_stars.stars


def get_general_stars_saler(cls):

    saler_stars = UserStart.objects.filter(saler=cls).aggregate(Avg('stars'))
    print(saler_stars)
    return int(saler_stars['stars__avg'])

def get_mys_products_actives(cls):

    products_actives = UserProduct.objects.filter(user=cls).filter(product__active = True)
    return products_actives

#trae subproductos comprados por el vendedor
def get_my_buy_subproducts_actives_by_product(cls, product):

    my_sub_products_actives = SubProduct.objects.filter(owner=cls, product=product, active=True)
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
        return money_saler
    else:
        return 0

def get_my_salers(cls):

    my_subproduct = list(SubProduct.objects.filter(owner = cls).values_list('creater_id', flat=True))
    my_salers = User.objects.filter(is_active=True, id__in= my_subproduct)
    return my_salers


User.add_to_class("get_general_stars_saler",get_general_stars_saler)
User.add_to_class("get_stars_saler",get_stars_saler)
User.add_to_class("get_my_salers",get_my_salers)
User.add_to_class("get_mys_products_actives",get_mys_products_actives)
User.add_to_class("add_money_user",add_money_user)
User.add_to_class("get_my_money",get_my_money)
User.add_to_class("subtract_money",subtract_money)
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