from django import forms
from django.forms import formset_factory

from .models import VIP, Project, Tag, EventTime, StaffProfile      

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

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']

class EventTimeForm(forms.Form):

    date = forms.DateField()
    start_time = forms.TimeField()
    end_time = forms.TimeField()
    # session = forms.ChoiceField(choices=EventTime.session_choices)
    session = forms.CharField(max_length=20)
    ticket_count = forms.IntegerField()
    location_name = forms.CharField(max_length=100)
    location_address = forms.CharField(max_length=200)
    dead_line_date = forms.DateField()
    dispatch_date = forms.DateField()
    announce_date = forms.DateField()      
    entry_time = forms.TimeField()
    section = forms.CharField(max_length=100)   
    
class BaseEventTimeFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            date = form.cleaned_data.get('date')
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')
            if date and start_time and end_time:
                if start_time >= end_time:
                    raise forms.ValidationError(
                        'Event time must be before end time.'
                    )
EventTimeFormSet = forms.formset_factory(EventTimeForm, formset=BaseEventTimeFormSet, extra=0)

class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ['phone_number', 'department']
        labels = {
            'phone_number': ('員工電話號碼：'),
            'department': ('員工部門：')
        }   