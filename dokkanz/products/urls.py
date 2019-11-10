from django.urls import path

from .views import (ListCreateCategory, ListCreateProduct,
                    RUDProduct, RUDCategory)


app_name = 'products'
urlpatterns = [
    path('create/category', view=ListCreateCategory.as_view(),
         name='create_category'),
    path('create/product', view=ListCreateProduct.as_view(),
         name='create_product'),
    path('rud/product/<code>',
         view=RUDProduct.as_view(),
         name='rud_product'),
    path('rud/category/<id>',
         view=RUDCategory.as_view(),
         name='rud_category'),

]
