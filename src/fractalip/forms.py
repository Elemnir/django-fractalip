import ipaddress

from django.forms               import ModelForm
from django.forms.utils         import ErrorList
from django.utils.html          import escape
from django.utils.safestring    import mark_safe

from .models    import Network, AddressBlock, Address


class BootstrapErrorList(ErrorList):
    def __str__(self):
        return self.as_alert()

    @mark_safe
    def as_alert(self):
        return ('<div class="alert alert-danger" role="alert">{}</div>'.format(
            ''.join(['<p class="error">{}</p>'.format(escape(e)) for e in self])
        ) if self else '')
    
    @mark_safe
    def as_p(self):
        return ''.join(['<p class="form-text">{}</p>'.format(escape(e)) for e in self]) if self else ''
        

class BootstrapModelForm(ModelForm):
    def __init__(self, *args, error_class=BootstrapErrorList, **kwargs):
        super().__init__(*args, error_class=error_class, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class NetworkForm(BootstrapModelForm):
    class Meta:
        model = Network
        fields = ("name", "notes", "admins", "network", "netmask", "vlan")


class AddressBlockForm(BootstrapModelForm):
    class Meta: 
        model = AddressBlock
        fields = ("name", "owner", "network", "start", "length", "notes")


class AddressForm(BootstrapModelForm):
    class Meta:
        model = Address
        fields = ("name", "ipblock", "address", "notes")

