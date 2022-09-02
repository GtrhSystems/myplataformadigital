from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group
from django.urls import resolve

def check_user_type(request):    

    if request.user.is_superuser:
        user_type = "superuser"
    else:
        groups = Group.objects.filter(user = request.user)       
        for group in groups:
            user_type = group.name
              
    return user_type                



def usertype_in_view(function):

    def wrap(request, *args, **kwargs):
        staff = ['saler-add',
                 'saler-list',
                 'delete-table-id',
                 'platforms-list',
                 'add-subproduct',
                 'edit-package',
                 'add-count-package',
                 'multiplatforms-sales',
                 'reported-issue',
                 'send-package-to-markeplace',
                 'market-place',
                 'my-packages-in-market-place',
                 'multiplatforms-sales-month',
                 'sales-inter-dates',
                 'general-sales',
                 'commission-collect',
                 'commission-payed',
                 'renew-count-package-list',
                 'renew-count-package'
                 ]
        vendedor = ['platforms',
                    'sale-count-package',
                    'buy-platform',
                    'multiplatforms-sales',
                    'report-issue-platform',
                    'delete-table-id',
                    'market-place',
                    'qualify-saler-list',
                    'qualify-saler',
                    'multiplatforms-sales-month',
                    'general-sales',
                    'buys-inter-dates',
                    'resale-count-package'
                    ]
        superuser = ['add-product',
                     'staff-list',
                     'activate-staff',
                     'check-username',
                     'activate-ajax-staff',
                     'delete-table-id',
                     'reported-issue',
                     'add-money-saler',
                     'money-saler-list',
                     'market-place',
                     'multiplatforms-sales',
                     'commision-pending',
                     'pay-staff-sale',
                     'multiplatforms-sales-month',
                     'sales-inter-dates',
                     'user-pay-pending',
                     'see-sale',
                     'pay-invoice-pendding'
                     ]
        request_url = request.__dict__['path_info'] #captura todo el request en un dict      
        match = resolve(request_url) #devuelve el name de la vista
        url_name = match.url_name
        user_type = check_user_type(request)
        if   url_name  in eval(user_type):
            return function(request, *args, **kwargs)        
        else:
            raise PermissionDenied    
       
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


