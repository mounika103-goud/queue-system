from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from queueapp.models import Token, Queue, Counter
from django.utils import timezone


class Command(BaseCommand):
    help = 'Add tokens to a customer user account'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the customer')
        parser.add_argument('--count', type=int, default=5, help='Number of tokens to add (default: 5)')
        parser.add_argument('--queue-id', type=str, help='Queue ID (optional, defaults to first available queue)')

    def handle(self, *args, **options):
        username = options['username']
        token_count = options['count']
        queue_id = options.get('queue_id')

        try:
            customer = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'Found user: {customer.username}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            return

        # Get or determine the queue
        if queue_id:
            try:
                queue = Queue.objects.get(queue_id=queue_id)
            except Queue.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Queue "{queue_id}" not found'))
                return
        else:
            # Use the first available queue
            queue = Queue.objects.first()
            if not queue:
                self.stdout.write(self.style.ERROR('No queues found in the system. Please create a queue first.'))
                return

        # Create tokens
        created_tokens = []
        for i in range(token_count):
            token_number = f"{customer.username}-{timezone.now().strftime('%Y%m%d%H%M%S')}-{i+1}"
            token = Token.objects.create(
                token_number=token_number,
                queue=queue,
                customer=customer,
                user=customer,
                status='generated',
                priority=1
            )
            created_tokens.append(token)
            self.stdout.write(self.style.SUCCESS(f'Created token: {token.token_number}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully added {len(created_tokens)} tokens to {customer.username}'))
