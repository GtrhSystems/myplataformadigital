from multiplataforma import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.IndexView, name='index'),
    path('set_cookie/<str:action>/<str:username>', views.LoginCookieView, name='login-cookie'),
    path('add-product', views.ProductCreateView, name='add-product'),
    #vendedores
    path('saler/add', views.CreateSalerView, name='saler-add'),
    path('saler/edit/<int:pk>', views.EditSalerView, name='saler-edit'),
    path('saler/list', views.SalerListView, name='saler-list'),
    #staffs
    path('staff/register', views.RegisterStaffView, name='staff-add'),
    path('service/check-username/<str:username>', views.CheckUsernameAjaxView, name='check-username'),
    path('<str:type>/list/<int:authorized>', views.StaffListView, name='staff-list'),
    path('<str:type>/activate/<int:pk>', views.ActivateStaffView, name='activate-staff'),
    path('user/add-money/<int:pk>', views.AddMoneySalerView, name='add-money-saler'),
    path('user/money-saler-list', views.MoneySalerListView, name='money-saler-list'),
    path('user/qualify-saler-list', views.QualifySalerListView, name='qualify-saler-list'),
    path('user/qualify-saler/<int:id>/<int:stars>', views.QualifySalerView, name='qualify-saler'),

    #plataformas-staff
    path('platform/list', views.PlatformListView, name='platforms-list'),
    #path('platform/add-subproduct/<str:id>', views.SubProductCreateView, name='add-subproduct'),
    path('add-subproduct/<int:id>', views.SubProductCreateView, name='add-subproduct'),
    path('edit-package/<int:id>', views.PackageEditView, name='edit-package'),
    path('add-count-package/<int:id>', views.AddCountToPackageView, name='add-count-package'),
    path('send-package-to-markeplace/<int:id>', views.SendPackageToMarketPlaceView, name='send-package-to-markeplace'),

    #multiplataformas-vendedor
    path('platform/market-place', views.MarketPlaceView, name='market-place'),
    path('platform/my-packages-in-market-place', views.MyPackageMerketPlaceView, name='my-packages-in-market-place'),
    path('platform/list/<str:name>', views.SalePlatformsView, name='platforms'),
    path('package/buy/<int:id>', views.BuyPackageView, name='buy-platform'),

    path('platform/report-issue/<str:platform>/<int:id>', views.ReportIssuePlatformView, name='report-issue-platform'),
    path('platform/issues-reported', views.ReportedIssuesView, name='reported-issues-platform'),
    path('platform/reported-issue/<int:id>', views.ReportedIssue, name='reported-issue'),
    #ventas
    path('package/sale-count/<int:id>', views.SaleCountView, name='sale-count-package'),
    path('platform/sales/month/<int:year>/<int:month>', views.SalesMonthPlatformsView, name='multiplatforms-sales-month'),
    path('platform/sales/general-sales', views.GeneralSalesView, name='general-sales'),
    path('platform/sales/pay-pending', views.CommissionPendingView, name='commision-pending'),
    path('platform/sales/pay-staff-sale/<int:id>', views.PayStaffSaleView, name='pay-staff-sale'),
    path('platform/sales/inter-dates', views.InterDatesSalesView, name='sales-inter-dates'),


    #Borrado de registros
    path('delete/<str:model>/<str:id>', views.DeleteRegister, name='delete-table-id'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)