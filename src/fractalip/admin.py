from django.contrib import admin

from .models    import Network, AddressBlock, Address


class NetworkAdmin(admin.ModelAdmin):
    pass
admin.site.register(Network, NetworkAdmin)


class AddressBlockAdmin(admin.ModelAdmin):
    pass
admin.site.register(AddressBlock, AddressBlockAdmin)


class AddressAdmin(admin.ModelAdmin):
    pass
admin.site.register(Address, AddressAdmin)
