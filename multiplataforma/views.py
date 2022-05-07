from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, JsonResponse
from .decorators import usertype_in_view
from .forms import  *
from .models import *
from .libraries import *
from django.core.mail import send_mail, BadHeaderError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

PERCENT_COMISSION = 0
if PercentCommission.objects.all():
    PERCENT_COMISSION = PercentCommission.objects.all().first().percent


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

    user_type = check_user_type(request)
    stars = money = 0
    products_actives = None
    year =  date =datetime.date.today().strftime('%Y')
    month = datetime.date.today().strftime('%m')
    if user_type == 'vendedor':
        money = request.user.get_my_money()
        products_actives = request.user.get_mys_products_actives()
    elif user_type == 'staff':
        stars = request.user.get_general_stars_saler()
    context = {
        'year': year,
        'stars':stars,
        'month':month,
        'user_type': user_type,
        'products_actives': products_actives,
        'money': money,
    }
    return context


def LoginCookieView(request, action, username):

    #userdata = cookies.SimpleCookie()
    response = HttpResponse()
    if action == "remember":
        response.set_cookie("username", username)

    else:
        response.delete_cookie('username')
    return response


@login_required
def IndexView(request):

    user_type = check_user_type(request)
    if user_type == "superuser":
        salers_actives = len(User.objects.filter(is_active=True).filter(groups__name = "vendedor"))
        salers_requests = len(User.objects.filter(is_active=False).filter(groups__name = "vendedor"))
        staff_actives  = len(User.objects.filter(is_active=True).filter(groups__name = "staff"))
        staff_requests = len(User.objects.filter(is_active=False).filter(groups__name="staff"))
        return render(request, 'dashboard_'+user_type+'.html', {'salers_actives':salers_actives, 'salers_requests':salers_requests, 'staff_actives':staff_actives, 'staff_requests':staff_requests })
    elif user_type == "staff":
        date = datetime.datetime.today()
        sales = CountsPackage.SalesByStaffbyDate(request.user, int(date.strftime("%Y")), int(date.strftime("%m")))
        if sales:
            sales_sum = sales.aggregate(total_sales=Sum('price_buy'))
            comission = int(sales_sum['total_sales']) * (PERCENT_COMISSION * 0.01)
            return render(request, 'sales/sales.html', {'sales': sales, 'sales_sum': sales_sum, 'comission': comission, 'layout': True})
        return render(request, 'sales/sales.html', { 'layout': True})

    elif user_type == "vendedor":
        return redirect('market-place')




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

    from django.utils.crypto import get_random_string
    form = SignUpForm()
    form2 = UserDataForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST or None)
        form2 = UserDataForm(request.POST, request.FILES or None)
        if form.is_valid() and form2.is_valid():
            user = form.save(commit=False)
            user.is_active = 0
            user.save()
            UserData = form2.save(commit=False)
            UserData.user = user
            token = get_random_string(length=30)
            UserData.token_register = token
            UserData.save()
            group = Group.objects.get(name=request.POST['group'])
            user.groups.add(group)
            return redirect('email-validations-register', user.username)

    return render(request, 'users/add-staff.html', {'form': form , 'form2':form2 })



def EmailValidationRegisterView(request, username):

    from django.template.loader import render_to_string
    user = User.objects.get(username=username)
    userdata = UserData.objects.get(user=user)
    if userdata.token_register != "":
        subject = "Validación de correo mymultiplataforma.com"
        email_template_name = "mail/email-verification.txt"
        mail_data = {
            "email": user.email,
            #'domain': 'myplataformadigital.com',
            'domain': ' 162.240.66.189',
            'site_name': 'mymultiplataformadigital',
            "user": user,
            'token': userdata.token_register,
            'protocol': 'http',
            #'protocol': 'https',
        }
        content = render_to_string(email_template_name, mail_data)
        try:
            mailing = Mail()
            mailing.send(user.email, subject, content)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
    else:
        return HttpResponse('Token no existe.')
    return render(request, 'users/email-validations-register.html',{ "user":user })

def EmailVerificationView(request, token):

    try:
        userdata = UserData.objects.get(token_register=token)
        if userdata:
            user = User.objects.get(id=userdata.id)
            userdata.token_register = ""
            userdata.email_verified = True
            userdata.save()
        else:
            return HttpResponse('Error. token invalido.')
    except:
        return HttpResponse('Error. token invalido.')
    return render(request, 'users/email-verified.html',{ "user":user })

@usertype_in_view
@login_required
def ActivateStaffView(request, type,  pk):

    user =  User.objects.filter( id = pk)
    user_data = UserData.objects.filter(user = user.first()).first()
    products_actives = list(user.last().get_mys_products_actives().values_list('product_id', flat=True))
    products = Product.get_all_products()
    if request.method == 'POST':
        if user.last().is_active == 0:
            user.update(is_active=1)
            ActionUser.objects.create(user=request.user, action='Activó  usuario id: ' + str(pk))
        UserProduct.objects.filter(user=user_data.user).delete()
        for product in products:
            if str(product.id) in request.POST:
                UserProduct.objects.create(user=user_data.user, product=product)
        return redirect('staff-list', type, 1)
    return render(request, 'users/activate-staff.html', { 'user':user.last(), 'user_data':user_data ,'products':products,  'type': type, 'products_actives':products_actives})


@usertype_in_view
@login_required
def StaffListView(request, type, authorized):

    users = User.objects.filter(is_active=authorized).filter(groups__name = type)
    for user in users:
        userdata = UserData.objects.get(user=user)
        user.email_verified= userdata.email_verified
    return render(request, 'users/list.html', {'users': users, 'authorized':authorized, 'type':type})


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

    salers = User.objects.filter(is_active=1).filter(groups__name = 'vendedor')
    return render(request, 'users/saler_list.html', {'salers': salers})


@usertype_in_view
@login_required
def AddMoneySalerView(request, pk):

    form = AddMoneyForm(request.POST or None)
    saler = User.objects.filter(id = pk).filter(groups__name = 'vendedor').first()
    money = saler.get_my_money()
    if request.method == 'POST':
        if form.is_valid():
            saler.add_money_user(money, request.POST['money'], "Recarga de saldo")
            return redirect('staff-list','vendedor', 1)

    return render(request, 'money/add-money-saler.html', {'form': form, 'saler': saler, 'money':money })

@usertype_in_view
@login_required
def MoneySalerListView(request):

    money_saler = MoneysSaler.Get_mys_money_saler()
    return render(request, 'money/moneys-list.html', {'money_saler': money_saler})


#plataformas-staff

@usertype_in_view
@login_required
def PlatformListView(request):

    user = User.objects.get(id=request.user.id)
    products_actives = user.get_mys_products_actives()

    return render(request, 'platforms/platforms-list.html', {'products_actives': products_actives})


@usertype_in_view
@login_required
def SubProductCreateView(request, id):

    form = SubProductForm(request.POST or None)
    product = Product.objects.filter(id=id).first()
    subproducts = SubProduct.objects.filter(product_id=id, creater=request.user,  active=True)
    if request.method == 'POST':
        if form.is_valid():
            subproduct = form.save(commit=False)
            subproduct.owner = request.user
            subproduct.creater = request.user
            subproduct.product = product
            subproduct.save()
            return redirect('add-subproduct', id)

    return render(request, 'platforms/add_subproduct.html', {'form': form, 'product': product, 'subproducts': subproducts })



@usertype_in_view
@login_required
def PackageEditView(request, id):

    subproduct = SubProduct.objects.filter(creater=request.user, id=id, active=True).select_related('product').first()
    if not subproduct:
        return redirect('index')
    form = SubProductForm(request.POST or None, instance=subproduct)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            ActionUser.objects.create(user=request.user, action="Edito subproducto: " + str(request.POST['name']))
            return redirect('add-subproduct', subproduct.product_id)

    return render(request, 'platforms/edit_subproduct.html', {'form': form, 'subproduct': subproduct })


@usertype_in_view
@login_required
def AddCountToPackageView(request, id):

    subproduct = SubProduct.objects.filter(creater=request.user, id=id, active=True).select_related('product').first()
    if not subproduct:
        return redirect('index')
    form = PlanProductForm(request.POST or None)
    plans = CountsPackage.objects.filter(subproduct_id=id)
    if request.method == 'POST':
        if form.is_valid():
            plan = form.save(commit=False)
            plan.subproduct = subproduct
            plan.owner = request.user
            plan.save()
            #ActionUser.objects.create(user=request.user, action="Creo plan para subproducto: " + str(subproduct.name))
            return redirect('add-count-package', id)

    return render(request, 'platforms/add_plan.html', {'form': form,'subproduct': subproduct, 'plans': plans, 'id':id })


@usertype_in_view
@login_required
def SendPackageToMarketPlaceView(request, id):

    subproduct = SubProduct.objects.filter(creater=request.user, id=id, active=True, for_sale=0).first()
    if subproduct:
        subproduct.for_sale = 1
        subproduct.save()
        return HttpResponse("Paquete enviado a la tienda")
    else:
        return HttpResponse("Hubo un error")

#************************* vendedores ***************************************

@usertype_in_view
@login_required
def MarketPlaceView(request):
    context = context_app(request)
    if context['user_type'] == "vendedor":
        #my_money = context_app(request)['money']
        products_actives = request.user.get_mys_products_actives().values_list('product_id', flat=True)
        staff_actives = User.objects.filter(groups__name = 'staff', is_active= True).values_list('id', flat=True)
        packages_list = []
        packages = SubProduct.objects.filter(active=True, creater__in=staff_actives,
                                             for_sale=True).filter(product__in=products_actives).order_by('-date')
        #packages = SubProduct.objects.filter(active=True, price__lte=my_money, creater__in = staff_actives, for_sale=True).filter(product__in= products_actives ).order_by('-date')
        for package in packages:
            counts = CountsPackage.get_all_counts_package_no_sales(package)
            if len(counts) == 0:
                continue
            stars = package.creater.get_general_stars_saler()
            packages_list.append({ 'id': package.id, 'individual_sale': package.individual_sale, 'name': package.name, 'product': package.product ,
                                   'counts': len(counts) ,'price':package.price, 'creater_id':package.creater.id, 'creater': package.creater.first_name + " "+package.creater.last_name, 'stars':stars })
    else:
        packages_list = []
        packages = SubProduct.objects.filter(active=True, for_sale=True).filter(product__active=True).order_by('-date')
        for package in packages:
            counts = CountsPackage.get_all_counts_package_no_sales(package)
            if len(counts) == 0:
                continue
            stars = package.creater.get_general_stars_saler()
            mine = False
            if package.creater == request.user:
                mine = True
            packages_list.append(
                {'id': package.id, 'name': package.name, 'product': package.product, 'counts': len(counts), 'user_type':context['user_type'],
                 'price': package.price, 'creater_id': package.creater.id, 'creater': package.creater.first_name + " " + package.creater.last_name, 'mine':mine, 'stars':stars})

    return render(request, 'platforms/market_place.html', {'packages': packages_list})

@usertype_in_view
@login_required
def MyPackageMerketPlaceView(request):

    products_actives = list(request.user.get_mys_products_actives().values_list('product_id', flat=True))
    packages = SubProduct.objects.filter(active=True, creater=request.user,
                                         for_sale=True).filter(product_id__in=products_actives).order_by('-date')
    return render(request, 'platforms/packages_all_actives_list.html', {'packages': packages})



@usertype_in_view
@login_required
def SalePlatformsView(request, name):

    product = Product.objects.filter(name=name, active=True).first()
    my_subproducts = request.user.get_my_buy_subproducts_actives_by_product(product)
    data = []
    for subproduct in my_subproducts:
        packages = CountsPackage.get_mys_counts_package_no_sales(subproduct, request.user)
        if packages:
            count_packages = len(packages)
            plan_saler_product = {'id': subproduct.id, 'name': subproduct.name, 'price_unity': packages.first().price_buy,  "coun_packages": count_packages, "product_name": subproduct.product.name}
            data.append(plan_saler_product)

    return render(request, 'platforms/packages_to_sale.html', {'packages': data,'product':product})


@usertype_in_view
@login_required
def BuyPackageView(request, id):

    subproduct = SubProduct.objects.filter(id=id, active=True).select_related('product').first()
    counts = CountsPackage.objects.filter(subproduct_id=subproduct.id, owner = subproduct.creater)
    if subproduct and len(counts) > 0:
        money_user = request.user.get_my_money()
        if money_user:
            if subproduct.price > money_user:
                return HttpResponse("No tienes suficiente saldo para esta transacción")
            else:
                if subproduct.individual_sale:
                    count = counts.last()
                    count.owner = request.user
                    count.price_buy = subproduct.price
                    count.commission = int(subproduct.price ) * (PERCENT_COMISSION * 0.01)
                    count.date_buy = datetime.datetime.now()
                    count.save()
                else:
                    subproduct.for_sale=0
                    subproduct.save()
                    len_counts = len(CountsPackage.objects.filter(subproduct_id=subproduct.id))
                    individual_price = subproduct.price/len_counts
                    commission = int(individual_price) * (PERCENT_COMISSION * 0.01)
                    counts.update(owner=request.user, date_buy =datetime.datetime.now(),price_buy = individual_price, commission=commission)
                    count = None
                request.user.subtract_money(money_user, subproduct.price , "Compra: " + str(subproduct.name) + " a " + subproduct.creater.username)
                if subproduct.individual_sale:
                    return render(request, 'platforms/sale_plan.html',  { 'subproduct': subproduct, 'count':count })
                else:
                    return HttpResponse("Paquete adquirido, todo el paquete aparecera a su nombre")

        return HttpResponse("No tienes suficiente saldo para esta transacción")
    else:
        return HttpResponse("Este plan no está disponible en este momento")

@usertype_in_view
@login_required
def SaleCountView(request, id):

    subproduct = SubProduct.objects.filter(id=id, active=True).first()
    if request.method == 'POST':
        last_count_package = CountsPackage.get_mys_counts_package_no_sales(subproduct, request.user).last()
        last_count_package.sale_count(request.POST['price'])
        #CountPackageSale.objects.create(saler =request.user, counts_package = last_count_package, price = request.POST['price'] )
        return redirect('platforms', subproduct.product.name)

    return render(request, 'sales/sale_count_box.html',{ 'id':id, 'subproduct':subproduct})

@usertype_in_view
@login_required
def SalesMonthPlatformsView(request, year=None, month= None):

    context = context_app(request)
    if context['user_type'] == "staff":
        template = 'sales/sales_no_layout.html'
        sales_sum = comission = 0
        sales =  CountsPackage.SalesByStaffbyDate(request.user, year, month)
        if sales:
            sales_sum = sales.aggregate(total_sales=Sum('price_buy'))
            comission = int(sales_sum['total_sales']) * (PERCENT_COMISSION*0.01)
            return render(request, template, {'sales': sales, 'sales_sum': sales_sum, 'comission': comission})

    elif context['user_type'] == "superuser":
        template = 'sales/sales_staff.html'
        sales = CountsPackage.SalesAllbyDate( year, month)
        if sales:
            sales_sum = sales.aggregate(total_sales=Sum('price_buy'))
            comission_sum =  sales.aggregate(total_commission=Sum('commission'))
            return render(request, template, {'sales': sales, 'sales_sum': sales_sum, 'comission': comission_sum['total_commission']    })



    elif context['user_type'] == "vendedor":
        template = 'sales/sales_saler.html'
        sales = CountsPackage.all_counts_saled_in_dates(year, month, request)
        sales_sum =  0
        if sales:
            sales_sum = sales.aggregate(total_sales=Sum('price_sale'))
            return render(request, template, {'sales': sales, 'sales_sum': sales_sum })

    return render(request, template)

@usertype_in_view
@login_required
def GeneralSalesView(request):

    context = context_app(request)
    if context['user_type'] == "staff":
        mys_general_sales = request.user.get_my_general_sales()
        sales_sum = comission = 0
        if mys_general_sales:
            sales_sum = mys_general_sales.aggregate(total_sales=Sum('price_buy'))
            comission = int(sales_sum['total_sales']) * (PERCENT_COMISSION * 0.01)

        return render(request, 'sales/sales_generals.html', {'sales': mys_general_sales, 'sales_sum': sales_sum, 'comission': comission})

    elif context['user_type'] == "vendedor":

        sales = CountsPackage.objects.filter(saled=1).filter(owner = request.user)
        sales_sum = 0
        if sales:
            sales_sum = sales.aggregate(total_sales=Sum('price_sale'))
            total_buy = sales.aggregate(total_buy=Sum('price_buy'))
            total_win =  float(sales_sum['total_sales'])-float(total_buy['total_buy'])

        return render(request, 'sales/sales_saler.html', {'sales': sales, 'sales_sum': sales_sum, 'total_win':total_win})



@usertype_in_view
@login_required
def InterDatesSalesView(request):

    context = context_app(request)
    form = GetInterDatesForm()
    return render(request, 'sales/inter-dates.html', {'form': form })


@usertype_in_view
@login_required
def CommissionPendingView(request):

    sales = CountsPackage.SalesPendingCommission()
    sales_sum = comission = 0
    if sales:
        sales_sum = sales.aggregate(total_sales=Sum('price_buy'))
        comission = int(sales_sum['total_sales']) * (PERCENT_COMISSION*0.01)

    return render(request, 'sales/sales_comission_pending.html',  {'sales': sales, 'sales_sum': sales_sum, 'comission': comission})

@usertype_in_view
@login_required
def PayStaffSaleView(request, id):

    sale = CountsPackage.objects.filter(id=id, commission_payed=0).first()

    if sale:
        user_data = UserData.objects.filter(user=sale.subproduct.creater).first()
        sale_pay = sale.SetPayStaffSale()
        return render(request, 'platforms/pay_staff_sale.html',  {'sale_pay': sale_pay, 'user_data':user_data})
    else:

        return HttpResponse("Este pago ya fue generado anteriormente o no existe")


@usertype_in_view
@login_required
def ReportIssuePlatformView(request, platform, id):

    sale = PlanPlatformSales.objects.filter(id=id).first()
    if sale.saler_id == request.user.id:
        form = ReportIssueForm()
        if request.method == 'POST':
            form = ReportIssueForm(request.POST)
            report = form.save(commit=False)
            report.user = request.user
            report.email = sale.email
            report.platform = platform
            report.is_active = 1
            report.save()
            return redirect('reported-issues-platform')
        return render(request, 'reports/plataform.html', {"form": form, 'sale': sale, 'platform': platform})
    else:
        return redirect('index')


@usertype_in_view
@login_required
def QualifySalerListView(request):

   my_salers = request.user.get_my_salers()
   salers=[]
   for my_saler in my_salers:
       user_data = UserData.objects.filter(user = my_saler).first()
       stars = my_saler.get_stars_saler(request.user)
       salers.append({'id': my_saler.id, 'image':user_data.image.url, 'first_name':my_saler.first_name ,'last_name':my_saler.last_name, 'stars': stars})
   return render(request, 'users/qualify-saler-list.html', {'my_salers': salers })

@usertype_in_view
@login_required
def QualifySalerView(request, id, stars):

   saler_starts = UserStart.objects.filter(buyer=request.user, saler_id=id).first()
   if saler_starts:
       saler_starts.stars = stars
       saler_starts.save()
   else:
       UserStart.objects.create(buyer=request.user, saler_id=id, stars=stars)
   return HttpResponse("Tu calificación fue registrada")


@login_required
def ReportedIssuesView(request):

    context = context_app(request)
    if context['user_type']== "superuser":
        reports = IssuesReport.objects.filter(state=0).order_by('state')
    elif context['user_type']== "staff":
        mys_salers_list = list(SalerStaff.My_salers(request.user)).values_list('saler', flat=True)
        reports = IssuesReport.objects.filter(user_id__in=mys_salers_list, state=0).order_by('state')
    elif context['user_type'] == "vendedor":
        reports = IssuesReport.objects.filter(user=request.user).order_by('state')
    return render(request, 'reports/list.html', {"reports": reports })

@usertype_in_view
@login_required
def ReportedIssue(request, id):

    context = context_app(request)
    if context['user_type'] == "superuser" or context['user_type'] == "staff":
        report = get_object_or_404(IssuesReport, pk=id)
        form = ReportForm(instance=report)
        if request.method == 'POST':
            state = False
            if 'state' in request.POST and request.POST['state'] == "on":
                state = True
            IssuesReport.objects.filter(id=id).update(state=state, response=request.POST['response'])
            return redirect('reported-issues-platform')

    else:
        return redirect('reported-issues-platform')

    return render(request, 'reports/edit.html', {"report": report, "form": form})


#delete
@usertype_in_view
@login_required
def DeleteRegister(request, model, id):

    user_type = check_user_type(request)
    if user_type == "superuser":
        models = ["User", "Product"]
    elif user_type == "staff":
        models = ["User", "CountsPackage", "SubProduct"]
    elif user_type == "vendedor" :
        models = ['IssuesReport']
    else:
        return redirect('index')
    if model in models:
        try:
            if model == "User":
                if user_type == "staff":
                    is_my_saler = SalerStaff.Is_my_saler(request.user.id, id)
                    if not is_my_saler:
                        return redirect('index')
                eval(model + ".objects.filter(id=" + id + ").update(is_active=0)")
                action = "Borrado de " + model + " con id: " + str(id)
                message = "Desactivado satisfactorio"
            else:
                if model == "SubProduct" or model == "Product":
                    exist_id = eval(model + ".objects.filter(id=" + id + ").first() ")
                elif model == "CountsPackage":
                    exist_id = eval(model + ".objects.filter(id=" + id + ").select_related('subproduct').first() ")
                    if exist_id.subproduct.owner_id != request.user.id:
                        exist_id = None
                elif model == "PlanPlatformSales":
                    exist_id = eval(model + ".objects.filter(id=" + id + ", saler_id=request.user.id)")
                else:
                    exist_id = eval( model + ".objects.filter(id=" + id + ", user_id=" + str(request.user.id) + ").first() ")
                if exist_id is None:
                    action = "Intento de borrado de " + model + " con id: " + str(id)
                    message = "No tienes acceso, esta acción será reportada"
                if model == "CountsPackage" :
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
