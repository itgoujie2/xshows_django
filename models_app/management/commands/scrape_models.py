"""
Management command to manually test scraping from different platforms.
Usage: python manage.py scrape_models <platform> [--limit 100]
"""
from django.core.management.base import BaseCommand
from models_app.tasks import (
    update_chaturbate_data,
    update_stripcash_data,
    update_xlovecash_data,
    update_bongacash_data,
    scrape_all_platforms
)


class Command(BaseCommand):
    help = 'Scrape model data from streaming platforms'

    def add_arguments(self, parser):
        parser.add_argument(
            'platform',
            type=str,
            choices=['chaturbate', 'stripcash', 'xlovecash', 'bongacash', 'all'],
            help='Platform to scrape'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Number of models to fetch (default: 100)'
        )

    def handle(self, *args, **options):
        platform = options['platform']
        limit = options['limit']

        self.stdout.write(f"Scraping {limit} models from {platform}...")

        if platform == 'chaturbate':
            update_chaturbate_data(limit)
        elif platform == 'stripcash':
            update_stripcash_data(limit)
        elif platform == 'xlovecash':
            update_xlovecash_data(limit)
        elif platform == 'bongacash':
            update_bongacash_data(limit)
        elif platform == 'all':
            scrape_all_platforms(limit)

        self.stdout.write(self.style.SUCCESS(f'✓ Scraping completed for {platform}'))
