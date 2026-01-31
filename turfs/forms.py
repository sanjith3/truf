from django import forms
from .models import Turf, SportType

class TurfForm(forms.ModelForm):
    class Meta:
        model = Turf
        fields = ['name', 'description', 'address', 'city', 'price_per_hour', 'sports', 'amenities']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-500 outline-none'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-500 outline-none', 'rows': 4}),
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-500 outline-none', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-500 outline-none'}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-500 outline-none'}),
            'sports': forms.CheckboxSelectMultiple(attrs={'class': 'flex gap-4'}),
            'amenities': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-brand-500 outline-none', 'placeholder': 'e.g. Floodlights, Parking, Water'}),
        }

class TurfImageForm(forms.Form):
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'w-full'}))
    is_cover = forms.BooleanField(required=False)
