from rest_framework import serializers

from .models import Category, Product


class ListCategorySerializer(serializers.ModelSerializer):
    """
    A serializer that used with Category model during listing it.
    enables nesting categories view as a tree structure.
    """
    class Meta:
        model = Category
        fields = ['name', 'child_category']

    # A function that performs nesting tree structure's view
    def get_fields(self):
        fields = super(ListCategorySerializer, self).get_fields()
        fields['child_category'] = ListCategorySerializer(many=True)
        return fields


class CreateCategorySerializer(serializers.ModelSerializer):
    """
    A serializer that used with Category model during creating new object
    """

    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """
    A serializer that used with Product model during creating new object
    """
    class Meta:
        model = Product
        exclude = ['id', 'categories']


class ListProductSerializer(serializers.ModelSerializer):
    """
    A serializer that used with Product model during listing it.
    """
    class Meta:
        model = Product
        exclude = ['id', 'quantity', 'categories']


