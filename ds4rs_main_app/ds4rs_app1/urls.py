from django.urls import path

from . import views

# print('This is from dashboardapp')

urlpatterns = [
    path('', views.index, name='ds4rs-home'),
    path('about/', views.about, name='ds4rs-about'),
    path('ndbi/', views.ndbi.index, name='ds4rs-ndbi'),
    path('ndbi/chart', views.ndbi.getNdbiChart, name='ds4rs-ndbi-chart'),
    path('ndvi/', views.ndvi, name='ds4rs-ndvi'),
    path('lulc/', views.lulc, name='ds4rs-lulc'),
    # path('post_ndbi_data/', views.post_ndbi_data, name='ds4rs-post_ndbi_data'),
]