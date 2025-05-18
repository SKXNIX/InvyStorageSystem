from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ReportForm
from .report_utils.csv_generator import (
    generate_current_stock,
    generate_low_stock,
    generate_operations,
    generate_product_operations
)
from .report_utils.pdf_generator import (
    generate_current_stock_pdf
)

class ReportView(LoginRequiredMixin, FormView):
    template_name = 'reports/report_form.html'
    form_class = ReportForm
    success_url = reverse_lazy('reports:generate')  # Указываем URL для перенаправления
    
    def form_valid(self, form):
        report_type = form.cleaned_data['report_type']
        format = form.cleaned_data['format']
        
        if report_type == 'current_stock':
            if format == 'csv':
                return generate_current_stock()
            else:
                return generate_current_stock_pdf()
        
        elif report_type == 'low_stock':
            if format == 'csv':
                return generate_low_stock()
            
        
        elif report_type == 'operations':
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            if format == 'csv':
                return generate_operations(start_date, end_date)
            
        
        elif report_type == 'product_operations':
            product = form.cleaned_data['product']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            if format == 'csv':
                return generate_product_operations(product, start_date, end_date)
            else:
                return generate_product_operations_pdf(product, start_date, end_date)
        return super().form_valid(form)
    