from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
from dotenv import load_dotenv

class Command(BaseCommand):
    help = '创建一个预定义的超级用户'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username= os.getenv('SUPERUSER_USERNAME')).exists():

            load_dotenv()

            User.objects.create_superuser(
                os.getenv('SUPERUSER_USERNAME'),
                os.getenv('SUPERUSER_EMAIL'),
                os.getenv('SUPERUSER_PASSWORD')
            )
            self.stdout.write(self.style.SUCCESS('成功创建超级用户'))
        else:
            self.stdout.write(self.style.WARNING('超级用户已存在'))