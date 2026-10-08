from django import forms
from django.utils import timezone
from .models import Activity,Comment
class UploadForm(forms.ModelForm):
    file=forms.FileField(label='GPX track',help_text='Up to 2 MB. Include timestamps for distance and pace.')
    class Meta:model=Activity;fields=['title','sport','date','public'];widgets={'date':forms.DateInput(attrs={'type':'date'})}
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.fields['date'].initial=timezone.localdate();self.fields['public'].help_text='Public activities share your full route with other signed-in members.'
    def clean_file(self):
        f=self.cleaned_data['file']
        if not f.name.lower().endswith('.gpx'):raise forms.ValidationError('Choose a .gpx file.')
        if f.size>2_000_000:raise forms.ValidationError('GPX files must be 2 MB or smaller.')
        return f
class CommentForm(forms.ModelForm):
    class Meta:model=Comment;fields=['text'];widgets={'text':forms.Textarea(attrs={'rows':3})}
