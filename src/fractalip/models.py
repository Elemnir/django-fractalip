import datetime
import ipaddress
import socket
import subprocess

from django.contrib.auth.models import User
from django.core.exceptions     import ValidationError
from django.core.validators     import MaxValueValidator
from django.db                  import models
from django.urls                import reverse
from django.utils.timezone      import now

class Network(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    active  = models.BooleanField(blank=True, default=True)
    name    = models.CharField(max_length=32, blank=True)
    notes   = models.TextField(blank=True)
    admins  = models.ManyToManyField(User, blank=True)
    network = models.GenericIPAddressField()
    netmask = models.GenericIPAddressField()
    vlan    = models.PositiveSmallIntegerField(
        blank=True, default=0, validators=[MaxValueValidator(4095)]
    )

    def __str__(self):
        rval = '{0} - '.format(self.name) if self.name else ''
        return rval + str(ipaddress.ip_network((self.network, self.netmask)))

    def clean(self):
        try:
            net = ipaddress.ip_network((self.network, self.netmask))
        except ValueError as e:
            raise ValidationError("Invalid Network or Netmask")

    def sentinel(self):
        return None


class AddressBlock(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    active  = models.BooleanField(blank=True, default=True)
    name    = models.CharField(max_length=32, blank=True)
    owner   = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    start   = models.GenericIPAddressField()
    length  = models.PositiveIntegerField(default=16, blank=True)
    notes   = models.TextField(blank=True)

    def __str__(self):
        rval = '{0} ({1})'.format(self.start, self.length)
        rval += ' - {0}'.format(self.name) if self.name else ''
        return rval

    def clean(self):
        """Prevent creation of a range extending beyond the block's network."""
        ipnet = ipaddress.ip_network((self.network.network, self.network.netmask))
        start_ip = ipaddress.ip_address(self.start)
        end_ip = start_ip + self.length
        for net in ipaddress.summarize_address_range(start_ip, end_ip):
            if not ipnet.overlaps(net):
                raise ValidationError(
                    'Subnet {0} between {1} and {2} is not a subnet of {3}'.format(
                        net, start_ip, end_ip, ipnet
                    )
                )
    
    def get_absolute_url(self):
        return reverse('fractalip:network-detail', args=[self.network.pk])
    
    def populate(self):
        """Perform a bulk creation of the IP Address objects within the block."""
        start_ip = ipaddress.ip_address(self.start)
        Address.objects.bulk_create(
            [ Address(ipblock=self, address=str(start_ip + i)) for i in range(self.length) ]
        )

    def sentinel(self):
        """Return the next IP address immediately following the block if such an 
        address exists within the block's network. Returns None if non-existent.
        """
        ipnet = ipaddress.ip_network((self.network.network, self.network.netmask))
        try:
            sentinel = ipaddress.ip_address(self.start) + self.length
        except Exception as e:
            return None
        if sentinel not in ipnet:
            return None
        return sentinel

    def lookup_names(self):
        """Attempts to resolve the Addresses within the block to a hostname"""
        for addr in self.address_set.all():
            addr.set_hostname_from_lookup()


class Address(models.Model): 
    created     = models.DateTimeField(auto_now_add=True)
    active      = models.BooleanField(blank=True, default=True)
    name        = models.CharField(max_length=32, blank=True)
    ipblock     = models.ForeignKey(AddressBlock, on_delete=models.CASCADE)
    address     = models.GenericIPAddressField()
    notes       = models.TextField(blank=True)
    last_ping   = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.address + ' - {0}'.format(self.name) if self.name else ''

    def get_absolute_url(self):
        return reverse('fractalip:network-detail', args=[self.ipblock.network.pk])

    def set_hostname_from_lookup(self):
        try:
            hostname, _, _ = socket.gethostbyaddr(self.address)
            self.name = hostname
        except:
            self.name = ''
        self.save()

    def ping_check(self):
        cmd = ["/usr/bin/ping", "-c", "1", self.address]
        if subprocess.call(cmd) == 0:
            self.last_ping = now()
            self.save()
            return True
        return False

    def pinged_recently(self):
        return (now() - self.last_ping) < datetime.timedelta(hours=1) if self.last_ping else False
