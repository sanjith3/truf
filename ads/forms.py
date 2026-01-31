from django import forms
from .models import AdCampaign

class AdCampaignForm(forms.ModelForm):
    class Meta:
        model = AdCampaign
        fields = [
            'advertiser_name', 'ad_type', 'placement', 'title', 
            'image', 'redirect_url', 'start_date', 'end_date', 
            'cost_model', 'cost_per_unit', 'daily_budget', 'total_budget'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input-brand'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input-brand'}),
            'advertiser_name': forms.TextInput(attrs={'placeholder': 'e.g. Nike, Local Sports Club', 'class': 'form-input-brand'}),
            'title': forms.TextInput(attrs={'placeholder': 'Catchy Headline', 'class': 'form-input-brand'}),
            'redirect_url': forms.URLInput(attrs={'placeholder': 'https://example.com', 'class': 'form-input-brand'}),
            'cost_per_unit': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input-brand'}),
            'daily_budget': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input-brand'}),
            'total_budget': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input-brand'}),
            'ad_type': forms.Select(attrs={'class': 'form-select-brand'}),
            'placement': forms.Select(attrs={'class': 'form-select-brand'}),
            'cost_model': forms.Select(attrs={'class': 'form-select-brand'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply shared classes if not using ad-hoc utilities
        shared_classes = "block w-full px-4 py-3 rounded-xl border-gray-200 focus:ring-brand-500 focus:border-brand-500"
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = shared_classes
            elif self.fields[field].widget.attrs['class'] in ['form-input-brand', 'form-select-brand']:
                self.fields[field].widget.attrs['class'] = shared_classes
