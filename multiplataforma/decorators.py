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
                 'saler-edit',
                 'add-money-saler',
                 'delete-table-id',
                 'money-saler-list',
                 'platforms-list',
                 'add-subproduct',
                 'edit-subproduct',
                 'add-plan-subproduct'
                 ]
        vendedor = ['platforms',
                    'sale-platform',

                    ]
        superuser = ['add-product',
                     'staff-list',
                     'activate-staff',
                     'check-username',
                     'activate-ajax-staff',
                     'delete-table-id'
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


