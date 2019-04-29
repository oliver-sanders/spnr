from django.db import models
from django.template.loader import render_to_string

from wagtail.core import blocks
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock


class FeatureBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    title = blocks.CharBlock(
        required=False,
        help_text=('An optional title to appear in the box. Leave blank if '
                   "you don't want it."))
    text = blocks.RichTextBlock()
    page = blocks.PageChooserBlock(required=False)

    class Meta:
        icon = 'title'
        label = 'Feature Block'
        template = 'feature.html'


class Highlight(blocks.StructBlock):
    image = ImageChooserBlock()
    page = blocks.PageChooserBlock()

    class Meta:
        icon = 'link'
        label = 'Highlight'


class HighlightsBlock(blocks.StructBlock):
    items = blocks.ListBlock(Highlight())

    class Meta:
        icon = 'link'
        label = 'Highlights'
        template = 'highlights.html'


class SectionBreak(blocks.StaticBlock):

    class Meta:
        icon = 'pilcrow'
        label = 'Section Break'
        template = 'section_break.html'

    def render_form(self, value, prefix='', errors=None):
        if self.meta.admin_text is None:
            return render_to_string('section_break_form.html')
        else:
            return self.meta.admin_text


#import blog.models


class BlogSummary(blocks.StructBlock):

    page = blocks.PageChooserBlock()
    # TODO: constrain to BlogIndexPage
    num_articles = blocks.IntegerBlock(default=2)

    class Meta:
        icon = 'mail'
        label = 'Blog Summary'
        template ='blog_summary.html'

    def get_context(self, request, parent_context=None):
        context = Page.get_context(self, request)
        page = Page.get_context(self, request)['request']['page']
        num_articles = Page.get_context(self, request)['request']['num_articles']
        posts = page.get_children().live().order_by('-first_published_at')
        context['posts'] = posts[:num_articles]
        return context


class HomePage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('feature', FeatureBlock()),
        ('highlights', HighlightsBlock()),
        ('section_break', SectionBreak()),
        ('blog_summary', BlogSummary()),
        ('paragraph', blocks.RichTextBlock(
            features=[
                'bold', 'italic', 'ol', 'ul', 'link', 'document-link',
                'embed', 'h3', 'h4'
            ]
        ))
    ], blank=True)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]


class NormalPage(HomePage):
    pass
