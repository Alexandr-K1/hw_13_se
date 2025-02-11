from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count

from bson.objectid import ObjectId
from .forms import AuthorForm, QuoteForm
from .models import Author, Quote, Tag
from .utils import get_mongodb, scrape_and_save_data
# Create your views here.

@login_required
def add_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Author added successfully!")
            return redirect('quotes:home')
    else:
        form = AuthorForm()

    return render(request, 'quotes/add_author.html', {'form': form})


@login_required
def add_quote(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Quote added successfully!")
            return redirect('quotes:home')
    else:
        form = QuoteForm()

    return render(request, 'quotes/add_quote.html', {'form': form})


def author_detail(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    quotes = Quote.objects.filter(author=author)
    return render(request, 'quotes/author_detail.html', {'author': author, 'quotes': quotes})


def quotes_by_tag(request, tag_name):
    quotes = Quote.objects.filter(tags__name=tag_name)
    return render(request, 'quotes/quotes_by_tag.html', {'quotes': quotes, 'tag_name': tag_name})


@login_required
def scrape_data(request):
    if request.method == "POST":
        scrape_url = request.POST.get('scrape_url')
        try:
            result = scrape_and_save_data(scrape_url)
            messages.success(request, result)
        except Exception as e:
            messages.error(request, f'Error during scraping: {e}')
        return redirect('quotes:home')

    return render(request, 'quotes/scrape.html')


def main(request, page=1):
    quotes = Quote.objects.all().order_by('-create_at')

    per_page = 10
    paginator = Paginator(quotes, per_page)
    quotes_on_page = paginator.page(page)

    top_tags = Tag.objects.annotate(num_quotes=Count('quote')).order_by('-num_quotes')[:10]

    return render(request, 'quotes/index.html', context={'quotes': quotes_on_page, 'top_tags': top_tags})