from django import forms
from apps.store.models import StockReceipt, Dispatch, Supplier


class StockReceiptForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.user and hasattr(instance, 'created_by'):
            instance.created_by = self.user
            
        if commit:
            instance.save()
        return instance

    class Meta:
        model = StockReceipt
        fields = ['product', 'quantity', 'receipt_date', 'invoice_number', 'supplier', 'status', 'comment']
        widgets = {
            'receipt_date': forms.DateInput(attrs={'type': 'date'})
            }

class StockReceiptStatusForm(forms.ModelForm):
    class Meta:
        model = StockReceipt
        fields = ['status']

class StockDispatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Dispatch
        fields = ['product', 'quantity', 'dispatch_date', 'invoice_number', 'recipient', 'status', 'comment']
        widgets = {
            'dispatch_date': forms.DateInput(attrs={'type': 'date'}),
            }

class StockDispatchStatusForm(forms.ModelForm):
    class Meta:
        model = Dispatch
        fields = ['status']

class SupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
    
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'website', 'notes'] 