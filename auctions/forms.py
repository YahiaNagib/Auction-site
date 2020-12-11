from django import forms
from django.forms import ModelForm
from .models import Listing, Category
from .fields import ListTextWidget


class AddListingForm(ModelForm):

    # categories = forms.ModelChoiceField(
    #     queryset=Category.objects.all(),
    #     label="Category",
    #     widget=forms.Select(
    #         attrs={'class': 'form-control form-control-lg mb-2'}),
    #     # initial=CategoryType.objects.get(pk=1)
    #     initial=""
    # )

    def __init__(self, *args, **kwargs):
        category_list = kwargs.pop('data_list', None)
        super(AddListingForm, self).__init__(*args, **kwargs)

        # the "name" parameter will allow you to use the same widget more than once in the same
        # form, not setting this parameter differently will cuse all inputs display the
        # same list.
        self.fields['category'].widget = ListTextWidget(
            data_list=category_list,
            name='category_list',
            attrs={'class': 'form-control form-control-lg mb-2', 'autocomplete': 'off'})
        self.fields['category'].required = False
        self.fields['image_URL'].required = False

    class Meta:
        model = Listing
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg mb-2', 'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-lg mb-2', 'autocomplete': 'off'}),
            'start_bid': forms.TextInput(attrs={'class': 'form-control form-control-lg mb-2', 'autocomplete': 'off'}),
            'image_URL': forms.TextInput(attrs={'class': 'form-control form-control-lg mb-2', 'autocomplete': 'off'}),
            # 'category': forms.Select(attrs={'class': 'form-control form-control-lg mb-2', 'autocomplete': 'off'}),
        }
        fields = ['title', 'description', 'start_bid', 'category', 'image_URL']