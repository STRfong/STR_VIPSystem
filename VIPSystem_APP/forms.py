from django import forms
from django.forms import formset_factory

from .models import VIP, Project, Tag, EventTime      

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
    event_date = forms.DateField()
    event_time = forms.TimeField()
    event_end_time = forms.TimeField()
    event_session = forms.ChoiceField(choices=EventTime.session_choices)
    ticket_count = forms.IntegerField()
    event_location = forms.CharField(max_length=100)
    event_address = forms.CharField(max_length=200)

class BaseEventTimeFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            event_date = form.cleaned_data.get('event_date')
            event_time = form.cleaned_data.get('event_time')
            event_end_time = form.cleaned_data.get('event_end_time')
            if event_date and event_time and event_end_time:
                if event_time >= event_end_time:
                    raise forms.ValidationError(
                        'Event time must be before end time.'
                    )
EventTimeFormSet = forms.formset_factory(EventTimeForm, formset=BaseEventTimeFormSet, extra=0)