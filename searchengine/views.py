from django.views.generic import ListView, FormView
from django.core.urlresolvers import reverse_lazy
from searchengine import graph_search
from django.shortcuts import render
from django.contrib import messages
from .forms import DocumentForm
from .models import Document
import hashlib


def search(request):
    error = False
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        if not q:
            error = True
        else:
            results = graph_search.main(q)
            return render(request, 'index.html',
                          {'results': results, 'query': q})
    return render(request, 'index.html', {'error': error})


class FileListView(ListView):
    model = Document
    queryset = Document.objects.order_by('-id')
    context_object_name = "files"
    template_name = "files.html"
    paginate_by = 5


class FileAddView(FormView):

    form_class = DocumentForm
    success_url = reverse_lazy('home')
    template_name = "add.html"

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, 'File uploaded!', fail_silently=True)
        return super(FileAddView, self).form_valid(form)


class FileAddHashedView(FormView):
    """This view hashes the file contents using md5"""

    form_class = DocumentForm
    success_url = reverse_lazy('home')
    template_name = "add.html"

    def form_valid(self, form):
        hash_value = hashlib.md5(form.files.get('f').read()).hexdigest()
        # form.save returns a new Document as instance
        instance = form.save(commit=False)
        instance.md5 = hash_value
        instance.save()
        messages.success(
            self.request, 'File hashed and uploaded!', fail_silently=True)
        return super(FileAddHashedView, self).form_valid(form)
