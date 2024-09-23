from django.core.management.base import BaseCommand
from VIPSystem_APP.models import Tag

class Command(BaseCommand):
    help = '創建預定義的標籤'

    def handle(self, *args, **options):
        tags = [
            '業務往來廠商',
            '潛在合作廠商',
            '政府機關',
            '政治團隊／人物',
            '影視圈',
            '音樂圈',
            '新媒體圈',
            '喜劇圈',
            '表演藝術圈',
            '其他娛樂產業圈',
            '媒體圈',
            '薩泰爾夥伴',
            '薩泰爾親友',
            '其他'
        ]

        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'成功創建標籤 "{tag_name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'標籤 "{tag_name}" 已存在'))

        self.stdout.write(self.style.SUCCESS('所有標籤創建完成'))