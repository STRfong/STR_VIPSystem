from django import forms

from .models import VIP, Project, Tag

class RawVIPForm(forms.Form): # 這個 form 是沒有跟 model 綁定的，所以沒有 save() 的功能
    name = forms.CharField()
    email = forms.CharField()

class InlineCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = 'VIPSystem/inline_checkbox_select.html'

class VIPForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=InlineCheckboxSelectMultiple,
        required=False,
        label='VIP 標籤：'
    )

    class Meta:
        model = VIP
        fields = '__all__'
        labels = {
            'name': ('VIP 姓名：'),
            'email' : ('VIP 電子郵件：'), 
            'phone_number': ('VIP 電話號碼：')
        }

# class ProjectForm(forms.ModelForm):
#     class Meta:
#         model = Project
        
#         fields = ['name', 'description', 'start_date', 'end_date']
#         labels = {
#             'name': ('專案名稱：'),
#             'description': ('專案描述：'),
#             'start_date': ('開始日期：'), 
#             'end_date': ('結束日期：')
#         }
#         widgets = {
#             'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#         }   