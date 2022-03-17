from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ActionUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=300, default="")
    date = models.DateTimeField(auto_now_add=True)


class City(models.Model):

    city = models.CharField(default="", max_length=100, verbose_name="Ciudad")

    def __str__(self):
        return self.city


class UserData(models.Model):

    user= models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=150, verbose_name="Dirección", default="")
    phones = models.CharField(max_length=150, verbose_name="Dirección", default="")
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    phones = models.CharField(max_length=150, verbose_name="Dirección", default="")
    observations = models.CharField(default="", max_length=255, verbose_name="Observaciones")



class Product(models.Model):

    name = models.CharField(max_length=150, verbose_name="Nombre", default="")
    active = models.BooleanField(default=1, verbose_name="Activo?:")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)

    def is_owner(cls, staff, id):
        is_owner = True if cls.owner == staff else False
        return is_owner


class SubProduct(models.Model):

    product = models.ForeignKey(Product, default=1, verbose_name="Plataforma", on_delete=models.CASCADE)
    name = models.CharField(max_length=150, verbose_name="Nombre", default="")
    price = models.IntegerField(default=0, verbose_name="Precio general", )
    renewable = models.BooleanField(default=0, verbose_name="Renovable?:")
    instructions = models.CharField(max_length=1000, verbose_name="Instrucciones", default="")
    active = models.BooleanField(default=1, verbose_name="Activo?")
    date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

    @classmethod
    def my_subproducts_authorized(self, saler, product):

        my_staff = SalerStaff.My_staff(saler)
        subproducts_my_staff = self.objects.filter(owner = my_staff.staff, product=product)
        return subproducts_my_staff


class PlansPlatform(models.Model):

    subproduct = models.ForeignKey(SubProduct, default=1, verbose_name="Producto", on_delete=models.CASCADE)
    email = models.CharField(max_length=100, verbose_name="Email")
    password = models.CharField(max_length=50, default="")
    profile = models.CharField(max_length=20, verbose_name="Perfil", default="")
    pin = models.CharField(max_length=4, verbose_name="Pin", default="0")

    def __str__(self):
        return str(self.email)


class SalerStaff(models.Model):

    saler = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saler")
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name="staff")

    @classmethod
    def My_salers(self, staff):

        my_salers = self.objects.filter(staff=staff)
        return my_salers

    @classmethod
    def My_staff(self, saler):

        my_staff = self.objects.filter(saler=saler).filter(staff__is_active=True).first()
        return my_staff

    @classmethod
    def Is_my_saler(self, staff_id, saler_id):
        saler_staff = self.objects.filter(saler_id=saler_id).filter(saler__is_active=True).first()
        if saler_staff and saler_staff.staff_id == staff_id:
            return True
        else:
            return False


class PriceSubproductSaler(models.Model):

    saler = models.ForeignKey(User, on_delete=models.CASCADE)
    subproduct = models.ForeignKey(SubProduct, on_delete=models.CASCADE, default="")
    price = models.IntegerField(default=0)

    def __str__(self):
        return str(self.subproduct) + " $"+str(self.price)

    @classmethod
    def Prices_by_salers(self, salers, subproduct):

        salers_prices = []
        for saler in salers:
            print(saler.id)
            saler_temps = User.objects.filter(id=saler.saler_id, is_active=True).first()
            price_saler = self.objects.filter(saler=saler_temps, subproduct=subproduct).first()
            if price_saler:
                price = price_saler.price
            else:
                price = subproduct.price
            if saler_temps:
                user_price = {"user_id": saler_temps.id, 'names': saler_temps.first_name + " " +  saler_temps.first_name,"user_name": saler_temps.username, "price": price}
                salers_prices.append(user_price)
        return salers_prices

class MoneysSaler(models.Model):

    saler = models.ForeignKey(User, verbose_name="Usuario", on_delete=models.CASCADE)
    detail = models.CharField(default="", verbose_name="Detalle", max_length=150)
    transaction_money = models.IntegerField(default=0, verbose_name="Comision")
    money = models.IntegerField(default=0, verbose_name="Dinero a agregar")
    date = models.DateTimeField(auto_now_add=True, null=True)

    def Subtract_money(cls, money_to_discount, detail):

        money_to_discount = int(money_to_discount)
        money = int(cls.money)
        if money >= money_to_discount:
            remains = money - money_to_discount
            if remains >= 0:
                MoneysSaler.objects.create(money=remains, saler=cls.saler, detail=detail,
                                          transaction_money=money_to_discount)
                return remains
        return False

    def Add_money_user(cls, transaction_money, detail):
        if cls:
            money = int(cls.money)
        else:
            money = 0
        transaction_money = int(transaction_money)
        if transaction_money > 0:
            remains = money + transaction_money
            MoneysSaler.objects.create(money=remains, saler_id=cls.saler_id, detail=detail,  transaction_money=transaction_money)
            return remains
        return False

    @classmethod
    def Get_money_saler(self, saler):

        money_saler = self.objects.filter(saler = saler).last()
        if money_saler:
            return money_saler
        else:
            return 0

    @classmethod
    def Get_mys_money_saler(self, staff):

        my_salers = list(SalerStaff.My_salers(staff).values_list('saler_id', flat=True))
        money_saler = self.objects.filter(saler_id__in=my_salers).select_related('saler')
        return money_saler

    def __str__(self):
        return str(self.money)

class PlanMultiplatformSales(models.Model):

    saler = models.ForeignKey(User, on_delete=models.CASCADE)
    subproduct = models.ForeignKey(SubProduct, on_delete=models.CASCADE, default="")
    price = models.IntegerField(default=0)
    email = models.CharField(max_length=150, default="")
    password = models.CharField(max_length=30, default="")
    profile = models.CharField(max_length=30, default="")
    pin = models.CharField(max_length=5, default="")
    date = models.DateTimeField(auto_now_add=True)
    update = models.BooleanField(default=1, verbose_name="Resuelto?:")
    date_limit = models.DateTimeField(verbose_name="Fecha de vencimiento", blank=True, null=True, auto_now_add=False)
    message_saler = models.CharField(max_length=150, default="")
    message_admin = models.CharField(max_length=150, default="")
    months = models.IntegerField(default=0)
    is_renovation = models.BooleanField(default=0, verbose_name="Es renovacion?:")
    accepted = models.BooleanField(default=1, blank=True, null=True, verbose_name="Aceptada?:")
    revised = models.BooleanField(default=0, verbose_name="Revisada?:")


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