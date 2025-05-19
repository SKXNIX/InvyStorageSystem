from abc import ABC, abstractmethod
from django.http import HttpResponse
from apps.products.models import Product
from apps.store.models import StockReceipt, Dispatch, Store
from django.db.models import Q, F

class BaseReportGenerator(ABC):
    @abstractmethod
    def generate(self, **kwargs):
        pass

    def get_current_stock_data(self):
        return Store.objects.select_related('product').all()

    def get_low_stock_data(self):
        return Product.objects.filter(quantity__lte=F('min_stock'))

    def get_operations_data(self, start_date, end_date):
        return {
            'receipts': StockReceipt.objects.filter(
                receipt_date__range=[start_date, end_date]
            ),
            'dispatches': Dispatch.objects.filter(
                dispatch_date__range=[start_date, end_date]
            )
        }

    def get_product_history_data(self, product, start_date, end_date):
        return {
            'product': product,
            'receipts': StockReceipt.objects.filter(
                product=product,
                receipt_date__range=[start_date, end_date]
            ),
            'dispatches': Dispatch.objects.filter(
                product=product,
                dispatch_date__range=[start_date, end_date]
            )
        }