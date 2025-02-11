from django import forms
from .models import Author, Quote, Tag


class AuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ['fullname', 'born_date', 'born_location', 'description']
        widgets = {
            'fullname': forms.TextInput(attrs={'class': 'form-control'}),
            'born_date': forms.TextInput(attrs={'class': 'form-control'}),
            'born_location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class QuoteForm(forms.ModelForm):

    class Meta:
        model = Quote
        fields = ['quote', 'author', 'tags']
        widgets = {
            'quote': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = Author.objects.all()
        self.fields['tags'].queryset = Tag.objects.all()