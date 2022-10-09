from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse


class StaticViewSitemap(Sitemap):
    def items(self):
        pages = [
                'main:index',
                'main:about',
                'main:review',
                'main:contact',
                'main:jobs',
                'main:faq',
                'main:tandc',
                'main:privacy',
                'main:sitemap',
            ]
        return pages

    def location(self, item):
        return reverse(item)
