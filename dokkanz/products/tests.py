from django.urls import reverse
from django.shortcuts import get_object_or_404

from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_204_NO_CONTENT,
)
from rest_framework.test import APITestCase

from .models import Category, Product


class CreateCategoryTest(APITestCase):
    @classmethod
    def setUp(cls):
        Category.objects.create(name='Sport', nesting_level=0)

    def test_parent_category_bad_request(self):
        url = reverse('products:create_category')
        data = {
            'name': '',
        }
        response = self.client.post(url, data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_child_category_bad_request(self):
        url = reverse('products:create_category')
        data = {
            'parent_name': 'Sport',
            'name': '',
        }
        response = self.client.post(url, data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_parent_category(self):
        url = reverse('products:create_category')
        data = {
            'name': 'Art',
        }
        response = self.client.post(url, data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_create_child_category(self):
        url = reverse('products:create_category')
        data = {
            'name': 'Football',
            'parent_name': 'Sport'
        }
        response = self.client.post(url, data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, HTTP_201_CREATED)


class CreateProductTest(APITestCase):
    @classmethod
    def setUp(cls):
        Category.objects.create(name='Sport', nesting_level=0)

    def test_product_no_categories_bad_request(self):
        url = reverse('products:create_product')
        data = {
            'categories': '',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_product_lack_of_data_bad_request(self):
        url = reverse('products:create_product')
        data = {
            'categories': 'Sport',
            'name': 'Ball',
            'code': '',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_product(self):
        url = reverse('products:create_product')
        data = {
            'categories': 'Sport',
            'name': 'Ball',
            'code': '20',
            'quantity': '25',
            'price': '50'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)


class RUDCategoryTest(APITestCase):
    @classmethod
    def setUp(cls):
        Category.objects.create(name='Sport', nesting_level=0)
        parent_category = get_object_or_404(Category, name='Sport')
        Category.objects.create(name='Football', parent=parent_category, nesting_level=1)

    def test_destroy_parent_category(self):
        parent_category = get_object_or_404(Category, name='Sport')
        url = reverse('products:rud_category', kwargs={'id': parent_category.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_destroy_child_category(self):
        child_category = get_object_or_404(Category, name='Football')
        url = reverse('products:rud_category', kwargs={'id': child_category.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
