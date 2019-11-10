import json

from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_204_NO_CONTENT,
)
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .serializers import (
    ListCategorySerializer,
    CreateCategorySerializer,
    ProductSerializer,
    ListProductSerializer
)
from .models import (
    Product, Category
)


class ListCreateCategory(ListCreateAPIView):
    """
    A class-based view that inherits ListCreateAPIView listing Category's
    objects in case of GET and Create a new object in case POST request
    """
    serializer_class = ListCategorySerializer
    queryset = Category.objects.filter(nesting_level=0)

    # A custom create method that overrides ListCreateAPIView's method.
    def create(self, request, *args, **kwargs):
        """
        A create method that overrides ListCreateAPIView's method, it accepts
        parent_name and name of the new category or only the name.
        """
        # To generate a mutable dictionary from QueryDict()
        requested_data = request.POST.copy()
        print(requested_data)
        # check if parent_name included in request
        if 'parent_name' in requested_data:
            parent_category = get_object_or_404(Category,
                                                name=request.POST['parent_name'])

            # Set the nesting_level of the new category
            requested_data['nesting_level'] = parent_category.nesting_level + 1
            serialized_category = CreateCategorySerializer(data=requested_data)
            if serialized_category.is_valid():
                category = Category.objects.create(
                    name=serialized_category.initial_data['name'],
                    parent=parent_category,
                    nesting_level=serialized_category.initial_data['nesting_level'],
                )
                category.save()
                # Use ListCategorySerializer to generate the returned
                # serialized data of the new category after saving it
                returned_serialized_category = ListCategorySerializer(category)
                return Response(returned_serialized_category.data,
                                status=HTTP_201_CREATED)
            else:
                return Response(serialized_category.errors,
                                status=HTTP_400_BAD_REQUEST)

        else:
            # Set the nesting_level to zero because the category itself
            # is a parent category
            requested_data['nesting_level'] = 0
            serialized_category = CreateCategorySerializer(data=requested_data)
            if serialized_category.is_valid():
                category = Category.objects.create(
                    name=serialized_category.initial_data['name'],
                    nesting_level=0,
                )
                category.save()
                # Use ListCategorySerializer to generate the returned
                # serialized data of the new category after saving it
                returned_serialized_category = ListCategorySerializer(category)
                return Response(returned_serialized_category.data,
                                status=HTTP_201_CREATED)
            else:
                return Response(serialized_category.errors,
                                status=HTTP_400_BAD_REQUEST)


class ProductListPaginator(PageNumberPagination):
    """
    A class that used to perform products pagination
    """
    page_size = 10
    page_size_query_param = 'page_size'


class ListCreateProduct(ListCreateAPIView):
    """
    A class-based view that inherits ListCreateAPIView listing Products's
    objects in case of GET and Create a new object in case POST request
    """
    serializer_class = ListProductSerializer
    pagination_class = ProductListPaginator

    def get_queryset(self):
        """
        Overriding ListCreateAPIView get_queryset method to get objects
        related to a specific category
        """
        category_name = self.request.GET.get('category')
        category = get_object_or_404(Category, name=category_name)
        products = Product.objects.filter(categories=category)
        return products

    def create(self, request, *args, **kwargs):
        """
        A create method that overrides ListCreateAPIView's method, it accepts
        name, code, price, quantity and categories of the new product.
        """

        # Loading raw json data from the request body
        requested_data = json.loads(request.body.decode('utf-8'))
        # Get a queryset of objects that have the same names of requested category
        categories = Category.objects.filter(name__in=list(requested_data['categories']))
        # remove the categories items from requested_data
        requested_data.pop('categories', None)
        serialized_product = ProductSerializer(data=requested_data)
        if serialized_product.is_valid():
            product = Product.objects.create(
                code=serialized_product.initial_data['code'],
                name=serialized_product.initial_data['name'],
                price=serialized_product.initial_data['price'],
                quantity=serialized_product.initial_data['quantity'],
            )
            product.categories.add(*categories)
            product.save()
            returned_serialized_product = ListProductSerializer(product)
            return Response(returned_serialized_product.data,
                            status=HTTP_201_CREATED)
        else:
            return Response(serialized_product.errors,
                            status=HTTP_400_BAD_REQUEST)


class RUDProduct(RetrieveUpdateDestroyAPIView):
    """
    A class-based view that inherits RetrieveUpdateDestroyAPIView
    retrieving a Product object in case of GET, update in case of
    PATCH and destroy in case of DELETE
    """
    serializer_class = ProductSerializer
    lookup_field = 'code'

    def get_object(self):
        """
        A method that overrides get_object method to get object depending
        on code sent with the GET request
        """
        code = self.kwargs['code']
        return get_object_or_404(Product, code=code)


class RUDCategory(RetrieveUpdateDestroyAPIView):
    """
    A class-based view that inherits RetrieveUpdateDestroyAPIView
    retrieving a Category object in case of GET, update in case of
    PATCH and destroy in case of DELETE
    """
    serializer_class = CreateCategorySerializer
    lookup_field = 'name'

    def get_object(self):
        """
        A method that overrides get_object method to get object depending
        on code sent with the GET request
        """
        id = self.kwargs['id']
        return get_object_or_404(Category, id=id)

    def destroy(self, request, *args, **kwargs):
        """
        A method that overrides destroy method to prevent deleting objects
        used by other objects
        """
        instance = self.get_object()
        # Check if instance has related objects
        if instance.child_category.count():
            return Response({'error': _("This category is referenced to other objects "), },
                            status=HTTP_403_FORBIDDEN)
        else:
            self.perform_destroy(instance)
            return Response(status=HTTP_204_NO_CONTENT)



