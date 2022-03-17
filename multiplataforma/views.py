from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, JsonResponse
from .decorators import usertype_in_view
from .forms import  *
from .models import *
import datetime


@login_required
def check_user_type(request):
    if request.user.is_superuser:
        user_type = "superuser"
    else:
        groups = Group.objects.filter(user=request.user)
        for group in groups:
            user_type = group.name
    return user_type


def context_app(request):
    #messages = MessagesUser.get_messages_actives()
    user_type = check_user_type(request)
    money = 0
    if user_type == 'vendedor':
        money = MoneysSaler.Get_money_saler(request.user.id)
    products = Product.objects.filter(active=True)
    context = {
        'user_type': user_type,
        'products': products,
        'money': money,
    }
    return context


@login_required
def IndexView(request):
    return render(request, 'index.html')


@usertype_in_view
@login_required
def ProductCreateView(request):

    form = ProductForm(request.POST or None)
    products = Product.objects.filter(active=True)
    if request.method == 'POST':
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect('add-product')

    return render(request, 'platforms/add_product.html', {'form': form, 'products': products})



#**************************staff********************************************


def RegisterStaffView(request):

    form = SignUpForm(request.POST or None)
    form2 = UserDataForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = 0
            user.save()
            UserData = form2.save(commit=False)
            UserData.user = user
            UserData.save()
            group = Group.objects.get(name='staff')
            user.groups.add(group)
            return redirect('index')

    return render(request, 'users/add-staff.html', {'form': form , 'form2':form2 })

@usertype_in_view
@login_required
def ActivateStaffView(request, authorized, pk):

    staff =  User.objects.filter(is_active = authorized, id = pk).filter(groups__name = "staff").first()
    user_data = UserData.objects.filter(user = staff).first()
    return render(request, 'users/activate-staff.html', { 'staff':staff, 'user_data':user_data , 'authorized':authorized})


@usertype_in_view
@login_required
def StaffListView(request, authorized):

    staffs = User.objects.filter(is_active=authorized).filter(groups__name = "staff")
    return render(request, 'users/staffs_not_authorized.html', {'staffs': staffs, 'authorized':authorized})


@usertype_in_view
@login_required
def CheckUsernameAjaxView(request, username):

    username = User.objects.filter(username= username)
    if username:
        return HttpResponse("exits")
    else:
        return HttpResponse("not_exist")

@usertype_in_view
@login_required
def ActivateStaffAjaxView(request, pk):

    try:
        user = User.objects.filter(id=pk)
        user.update(is_active = 1 )
        return HttpResponse("True")
    except:
        return HttpResponse("False")



@usertype_in_view
@login_required
def CreateSalerView(request):

    form = SignUpForm(request.POST or None)
    form2 = UserDataForm( request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            UserData = form2.save(commit=False)
            UserData.user = user
            UserData.save()
            group = Group.objects.get(name='vendedor')
            user.groups.add(group)
            SalerStaff.objects.create(saler=user, staff=request.user)
            return redirect('saler-list')

    return render(request, 'users/add-saler.html', {'form': form , 'form2':form2 })


@usertype_in_view
@login_required
def EditSalerView(request, pk):

    from .models import UserData
    is_my_saler = SalerStaff.Is_my_saler(request.user.id, pk)
    if not is_my_saler:
        return redirect('index')
    user = get_object_or_404(User, pk=pk)
    form = EditUserForm(instance=user)
    user_data = UserData.objects.filter( user_id=pk).first()
    form2 = UserDataForm(instance=user_data)
    if request.method == 'POST':
        data = {'first_name': request.POST['first_name'], 'last_name': request.POST['last_name'],
                'email': request.POST['email'], 'is_active': request.POST['is_active'], 'password1': user.password,
                'password2': user.password}
        form = EditUserForm(data, instance=user)
        if form.is_valid():
                user = form.save()
                UserData = form2.save(commit=False)
                UserData.user = user
                UserData.save()
                return redirect('saler-list')

    return render(request, 'users/edit-saler.html', {'form': form , 'form2':form2 })



@usertype_in_view
@login_required
def SalerListView(request):

    salers = SalerStaff.objects.select_related('staff').filter(saler__is_active=1).filter(staff__id=request.user.id)
    return render(request, 'users/saler_list.html', {'salers': salers})


@usertype_in_view
@login_required
def AddMoneySalerView(request, pk):

    is_my_saler = SalerStaff.Is_my_saler(request.user.id, pk)
    if not is_my_saler:
        return redirect('index')
    form = AddMoneyForm(request.POST or None)
    saler = User.objects.get(id = pk)
    money_saler = MoneysSaler.Get_money_saler(saler)
    if money_saler == 0:
        money = money_saler
    else:
        money = money_saler.money
    if request.method == 'POST':
        if form.is_valid():
            if money_saler == 0:
                MoneysSaler.objects.create(money=money, saler=saler, detail="Recarga de saldo", transaction_money=money)
            else:
                money_saler.Add_money_user(request.POST['money'], "Recarga de saldo")
            return redirect('saler-list')

    return render(request, 'money/add-money-saler.html', {'form': form, 'saler': saler, 'money':money })

@usertype_in_view
@login_required
def MoneySalerListView(request):

    money_saler = MoneysSaler.Get_mys_money_saler(request.user)
    return render(request, 'money/moneys-list.html', {'money_saler': money_saler})


#plataformas-staff

@usertype_in_view
@login_required
def PlatformListView(request):

    platforms = Product.objects.filter(active=True)
    return render(request, 'platforms/platforms-list.html', {'platforms': platforms})


@usertype_in_view
@login_required
def SubProductCreateView(request, id):

    form = SubProductForm(request.POST or None)
    product = Product.objects.filter(id=id).first()
    my_salers = SalerStaff.My_salers( request.user)
    subproducts = SubProduct.objects.filter(product_id=id, active=True)
    if request.method == 'POST':
        if form.is_valid():
            subproduct = form.save(commit=False)
            subproduct.owner = request.user
            subproduct.product = product
            subproduct.save()
            for item in request.POST:
                if item.isnumeric():
                    PriceSubproductSaler.objects.create(price=request.POST[item], saler_id=item, subproduct_id=subproduct.id)
            return redirect('add-subproduct', id)

    return render(request, 'platforms/add_subproduct.html', {'form': form, 'product': product, 'subproducts': subproducts, 'salers': my_salers})



@usertype_in_view
@login_required
def SubProductEditView(request, id):

    subproduct = SubProduct.objects.filter(owner=request.user, id=id, active=True).select_related('product').first()
    if not subproduct:
        return redirect('index')
    form = SubProductForm(request.POST or None, instance=subproduct)
    my_salers = SalerStaff.My_salers( request.user)
    saler_price = PriceSubproductSaler.Prices_by_salers(my_salers, subproduct)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            for item in request.POST:
                if item.isnumeric():
                    plan_saler_price = PriceSubproductSaler.objects.filter(saler_id=item, subproduct_id=id)
                    if plan_saler_price:
                        plan_saler_price.update(price=request.POST[item])
                    else:
                        PriceSubproductSaler.objects.create(price=request.POST[item], saler_id=item, subproduct_id=subproduct.id)

            ActionUser.objects.create(user=request.user, action="Edito subproducto: " + str(request.POST['name']))
            return redirect('add-subproduct', subproduct.product_id)

    return render(request, 'platforms/edit_subproduct.html', {'form': form, 'subproduct': subproduct, 'salers': saler_price})


@usertype_in_view
@login_required
def PlanPlatformCreateView(request, id):

    subproduct = SubProduct.objects.filter(owner=request.user, id=id, active=True).select_related('product').first()
    if not subproduct:
        return redirect('index')
    form = PlanProductForm(request.POST or None)
    plans = PlansPlatform.objects.filter(subproduct_id=id)
    if request.method == 'POST':
        if form.is_valid():
            plan = form.save(commit=False)
            plan.subproduct = subproduct
            plan.save()
            #ActionUser.objects.create(user=request.user, action="Creo plan para subproducto: " + str(subproduct.name))
            return redirect('add-plan-subproduct', id)

    return render(request, 'platforms/add_plan.html', {'form': form,'subproduct': subproduct, 'plans': plans })


#************************* vendedores ***************************************

@usertype_in_view
@login_required
def PlatformsView(request, name):

    product = Product.objects.filter(name=name).first()
    data = []
    subproducts_my_staff = SubProduct.my_subproducts_authorized(request.user , product)
    for subproduct in subproducts_my_staff:
        plansaler = PriceSubproductSaler.objects.filter(saler=request.user, subproduct=subproduct).first()
        plancount = len(PlansPlatform.objects.filter(subproduct=subproduct))
        if plansaler:
            plan_saler_product = {'id': subproduct.id, 'name': subproduct.name, 'price': plansaler.price,  "conteo": plancount}
            data.append(plan_saler_product)

    return render(request, 'platforms/plans_product.html', {'subproducts': data, 'product': product})


@login_required
def SalePlatforms(request, id):

    plan = PlansPlatform.objects.filter(id=id).first()
    my_staff = SalerStaff.My_staff(request.user)
    subproduct = SubProduct.objects.filter(owner=my_staff.staff, id=plan.subproduct_id, active=True).select_related('product').first()
    if plan:
        money_user = MoneysSaler.Get_money_saler(request.user)
        if money_user:
            plansalerprice = PriceSubproductSaler.objects.filter(subproduct=subproduct, saler=request.user).first()
            if plansalerprice.price > money_user.money:
                return HttpResponse("No tienes suficiente saldo para esta transacción")
            else:
                remains = money_user.Subtract_money(plansalerprice.price , "Producto: " + str(subproduct.product.name) + " Subproducto: " + str( subproduct.name) + " Correo: " + plan.email)
                date_limit = datetime.datetime.now() + datetime.timedelta(days=30)
                PlanMultiplatformSales.objects.create(saler=request.user, subproduct=subproduct, price=plansalerprice.price,
                                                      email=plan.email, password=plan.password,
                                                      profile=plan.profile, pin=str(plan.pin),
                                                      date_limit=date_limit)
                plan.delete()
                return render(request, 'platforms/sale_plan.html',  {'plan': plan, 'subproduct': subproduct, 'product': subproduct.product})
        return HttpResponse("No tienes suficiente saldo para esta transacción")
    else:
        return HttpResponse("Este plan no está disponible en este momento")


#delete
@usertype_in_view
@login_required
def DeleteRegister(request, model, id):
    user_type = check_user_type(request)
    if user_type == "superuser":
        models = ["User", "Product", "SubProduct"]
    elif user_type == "staff":
        models = ["User", "Product","PlansPlatform"]
    elif user_type == "saler" or user_type == "resaler":
        models = []
    else:
        return redirect('index')
    if model in models:
        try:
            if model == "User":
                if user_type == "staff":
                    is_my_saler = SalerStaff.Is_my_saler(request.user.id, id)
                    print(is_my_saler)
                    if not is_my_saler:
                        return redirect('index')
                eval(model + ".objects.filter(id=" + id + ").update(is_active=0)")
                action = "Borrado de " + model + " con id: " + str(id)
                message = "Desactivado satisfactorio"
            else:
                if model == "SubProduct":
                    exist_id = eval(model + ".objects.filter(id=" + id + ").first() ")
                elif model == "PlansPlatform":
                    exist_id = eval(model + ".objects.filter(id=" + id + ").select_related('subproduct').first() ")
                    if exist_id.subproduct.owner_id != request.user.id:
                        exist_id = None
                elif model == "PlanMultiplatformSales":
                    exist_id = eval(model + ".objects.filter(id=" + id + ", saler_id=request.user.id)")
                else:
                    exist_id = eval(
                        model + ".objects.filter(id=" + id + ", admin=" + str(request.user.id) + ").first() ")
                if exist_id is None:
                    action = "Intento de borrado de " + model + " con id: " + str(id)
                    message = "No tienes acceso, esta acción será reportada"
                if model == "PlansPlatform" or model == "IssuesReport" or model == "PlanMultiplatformSales":
                    eval(model + ".objects.filter(id=" + id + ").delete()")
                else:
                    eval(model + ".objects.filter(id=" + id + ").update(active=0)")
                action = "Borrado de " + model + " con id " + str(id)
                message = "Desactivado satisfactorio"
        except ValueError:
            return HttpResponse(ValueError)
    else:
        action = "Intento de borrado de " + model + " con id: " + str(id)
        return HttpResponse("No tienes acceso, esta acción será reportada")
    ActionUser.objects.create(user=request.user, action=action)
    return HttpResponse(message)
