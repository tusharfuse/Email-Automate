import subprocess
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Install Playwright browsers'

    def handle(self, *args, **options):
        self.stdout.write('Running playwright install...')
        try:
            subprocess.check_call(['python', '-m', 'playwright', 'install'])
            self.stdout.write(self.style.SUCCESS('Playwright browsers installed successfully.'))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f'Error installing Playwright browsers: {e}'))
            raise e
