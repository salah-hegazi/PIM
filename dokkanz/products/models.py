from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class Category(models.Model):
    """
    A model that represents categories
    """
    # Describes what is the parent the category
    # if it has a nesting level value greater than zero
    parent = models.ForeignKey('self', default=None, null=True, blank=True,
                               on_delete=models.PROTECT,
                               related_name='child_category')
    # Identifying the level of the category
    # if zero then this is parent category
    nesting_level = models.IntegerField(_("Level of category"))
    name = models.CharField(_("Name of category"), max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    A model that represents products
    """
    code = models.CharField(_("Code of product"), max_length=10, unique=True)
    name = models.CharField(_("Name of product"), max_length=100)
    # representing a price as decimal and validate it against minus values
    price = models.DecimalField(_("Price of product"),
                                decimal_places=2, max_digits=8,
                                validators=[MinValueValidator(Decimal('0.01'))])
    quantity = models.PositiveIntegerField(_("Quantity of product"), default=0)
    categories = models.ManyToManyField(Category, related_name='products')

    def __str__(self):
        return self.name

