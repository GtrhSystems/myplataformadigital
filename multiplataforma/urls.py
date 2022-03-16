from multiplataforma import views
from django.urls import path



urlpatterns = [
    path('', views.IndexView, name='index'),
    path('add-product', views.ProductCreateView, name='add-product'),
    #vendedores
    path('saler/add', views.CreateSalerView, name='saler-add'),
    path('saler/edit/<int:pk>', views.EditSalerView, name='saler-edit'),
    path('saler/list', views.SalerListView, name='saler-list'),
    #staffs
    path('staff/register', views.RegisterStaffView, name='staff-add'),
    path('service/check-username/<str:username>', views.CheckUsernameAjaxView, name='check-username'),
    path('staff/list/<int:authorized>', views.StaffListView, name='staff-list'),
    path('staff/activate/<int:pk>', views.ActivateStaffView, name='activate-staff'),
    path('staff/activate-ajax/<int:pk>', views.ActivateStaffAjaxView, name='activate-ajax-staff'),
    path('staff/add-money-saler/<int:pk>', views.AddMoneySalerView, name='add-money-saler'),
    path('staff/money-saler-list', views.MoneySalerListView, name='money-saler-list'),
    #plataformas-staff
    path('platform/list', views.PlatformListView, name='platforms-list'),
    path('platform/add-subproduct/<int:id>', views.SubProductCreateView, name='add-subproduct'),
    path('add-subproduct/<int:id>', views.SubProductCreateView, name='add-subproduct'),
    path('edit-subproduct/<int:id>', views.SubProductEditView, name='edit-subproduct'),
    path('add-plan-subproduct/<int:id>', views.PlanPlatformCreateView, name='add-plan-subproduct'),


    #Borrado de registros
    path('delete/<str:model>/<str:id>', views.DeleteRegister, name='delete-table-id'),


]