from django.conf                    import settings
from django.contrib.auth.mixins     import LoginRequiredMixin, UserPassesTestMixin
from django.http                    import (HttpResponseBadRequest,
                                            HttpResponseForbidden)
from django.shortcuts               import get_object_or_404, redirect, render
from django.urls                    import reverse
from django.views.generic           import View, ListView, TemplateView
from django.views.generic.edit      import FormView, UpdateView

from .forms     import NetworkForm, AddressBlockForm, AddressForm
from .models    import Network, AddressBlock, Address


class NetworkCreateView(LoginRequiredMixin, FormView):
    form_class = NetworkForm

    def get(self, request):
        return HttpResponseForbidden() # No GET, only POST

    def form_valid(self, form):
        obj = form.save()
        obj.admins.add(self.request.user)
        return redirect(reverse('fractalip:network-list'))


class NetworkListView(LoginRequiredMixin, ListView):
    context_object_name = 'networks'
    template_name = 'network_list.html'
    paginate_by = 25
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addnetworkform'] = NetworkForm()
        return context

    def get_queryset(self):
        filters = {'active': True}
        for field in ['name', 'notes', 'network', 'netmask', 'vlan']:
            if field in self.request.GET and self.request.GET.get(field, ''):
                filters[field+'__icontains'] = self.request.GET[field]
        return Network.objects.filter(**filters).order_by('name', 'network')


class NetworkDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        network = get_object_or_404(Network, pk=pk)
        blocks = AddressBlock.objects.filter(active=True, network=network).order_by('start')
        return render(request, 'network_detail.html', {
            'network' : network,
            'blocks'  : blocks,
            'iplist'  : [ Address.objects.filter(active=True, ipblock=b).order_by('address') for b in blocks ],
            'netform' : NetworkForm(auto_id="netform-%s", instance=network),
            'addblockform' : AddressBlockForm(auto_id="addblock-%s")
        })

    def post(self, request, pk):
        network = get_object_or_404(Network, pk=pk)
        form = NetworkForm(request.POST, instance=network)
        if form.is_valid():
            form.save()    
        return redirect(reverse('fractalip:network-detail', args=[network.pk]))


class AddressBlockCreateView(LoginRequiredMixin, FormView):
    form_class = AddressBlockForm
    
    def get(self, request):
        return HttpResponseForbidden() # No GET, only POST

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        obj.populate()
        return redirect(reverse('fractalip:network-detail', args=[obj.network.pk]))

    def form_invalid(self, form):
        return HttpResponseBadRequest()


class AddressBlockDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        block = get_object_or_404(AddressBlock, pk=pk)
        if block.owner != request.user or request.user not in block.network.admins.all():
            return HttpResponseForbidden()
        block.active = False
        block.save()
        return redirect(reverse('fractalip:network-detail', args=[block.network.pk]))


class AddressBlockUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AddressBlock
    modelform = AddressBlockForm
    fields = [ "name", "notes" ]

    def test_func(self):
        return self.request.user

    def get(self, request):
        return HttpResponseForbidden() # No GET, only POST

    def form_invalid(self, form):
        return HttpResponseBadRequest()

    def form_valid(self, form):
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Address
    modelform = AddressForm
    fields = [ "name", "notes" ]

    def test_func(self):
        return self.request.user

    def get(self, request):
        return HttpResponseForbidden() # No GET, only POST

    def form_invalid(self, form):
        return HttpResponseBadRequest()

    def form_valid(self, form):
        return super().form_valid(form)
