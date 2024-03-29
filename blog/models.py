import calendar
import re

from django import forms
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet


HTML_REGEX = re.compile(r'<[^>]+>')


def get_extract(self, length=80):
    body = HTML_REGEX.sub('', self.body)  # crude strip HTML
    if body:
        for ind in range(min(len(body), length) - 1, 0, -1):
            if body[ind] in [' ', '.', ',']:
                break
        return '%s ...' % body[:ind]
    else:
        return ''

def get_main_image(self):
    image = None
    if hasattr(self, 'image'):
        image = self.image
    elif hasattr(self, 'gallery_images'):
        gallery = self.gallery_images.first()
        if gallery:
            image = gallery.image
    return image

def gallery_chunks(self, chunks=4):
    ret = []
    if getattr(self, 'gallery_images', None):
        imgs = self.gallery_images.all()
        ret = [imgs[x::chunks] for x in range(chunks)]
    return ret


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request, per_page=14):
        # Update context to include only published posts, ordered by 
        # reverse-chron
        context = Page.get_context(self, request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        paginator = Paginator(blogpages, per_page)
        page = request.GET.get('page')
        if page:
            page = int(page)
        else:
            page = 1
        try:
            blogpages = paginator.page(page)
        except PageNotAnInteger:
            blogpages = paginator.page(1)
        except EmptyPage:
            blogpages = paginator.page(paginator.num_pages)
        context['blogpages'] = blogpages
        context['page_num'] = page
        context['num_pages'] = paginator.num_pages
        context['pages'] = range(1, paginator.num_pages + 1)
        return context


class BlogPage(Page):

    date = models.DateField("Post date")
    image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
        help_text=('This image will appear at the top of the page.'))
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        ImageChooserPanel('image'),
        FieldPanel('body', classname="full"),
        InlinePanel('gallery_images', label="Photo Gallery"),
    ]

    get_extract = get_extract

    get_main_image = get_main_image

    gallery_chunks = gallery_chunks


class YearInPhotosPage(Page):

    NAME = 'Year In Photos'

    date = models.DateField("Post date")
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    content_panels = [
        # dont append to parent's content panels to remote the title field
        FieldPanel('date'),
        FieldPanel('body', classname="full"),
        InlinePanel('gallery_images', label="Photo Gallery"),
    ]

    get_extract = get_extract

    get_main_image = get_main_image

    gallery_chunks = gallery_chunks

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        if not self.title:
            self.set_title()

    def get_grid(self):
        """Return year in photos year-month grid."""
        grid = {}
        pages = self.get_parent().get_children().type(YearInPhotosPage).live()
        for page in pages:
            blogpage = page.yearinphotospage
            year, month = blogpage.date.year, blogpage.date.month
            grid.setdefault(year, [None] * 12)
            grid[year][month - 1] = page
        return grid

    def set_title(self):
        name = self.NAME
        if self.date:
            name += ' %s %s' % (
                calendar.month_name[self.date.month], self.date.year)
        self.title = name

    def save(self, *args, **kwargs):
        """Derive the page title from the date.

        Note the slug is derived also but this is done live using JS, see
        wagtail_hooks.py
        """
        self.set_title()
        Page.save(self, *args, **kwargs)

    #def serve_preview(self, *args, **kwargs):
    #    self.set_title()
    #    return Page.serve_preview(self, *args, **kwargs)


class BlogPageGalleryImage(Orderable):

    page = ParentalKey(
        Page, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = RichTextField(
        blank=True,
        features=[
            'bold', 'italic', 'ol', 'ul', 'link', 'document-link', 'embed']
    )

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]
