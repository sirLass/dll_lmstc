from django.core.management.base import BaseCommand
from Applicant.models import DocumentCategory


class Command(BaseCommand):
    help = 'Create initial document categories for manuals and policies'

    def handle(self, *args, **options):
        # Manual categories
        manual_categories = [
            {
                'name': 'Training Materials',
                'category_type': 'manual',
                'description': 'Training guides, course materials, and learning resources'
            },
            {
                'name': 'Equipment Manuals',
                'category_type': 'manual',
                'description': 'Equipment operation guides and maintenance manuals'
            },
            {
                'name': 'Safety Procedures',
                'category_type': 'manual',
                'description': 'Safety protocols, emergency procedures, and workplace safety guidelines'
            },
            {
                'name': 'Assessment Guides',
                'category_type': 'manual',
                'description': 'Assessment criteria, evaluation forms, and testing procedures'
            },
            {
                'name': 'Technical Standards',
                'category_type': 'manual',
                'description': 'Industry standards, technical specifications, and quality guidelines'
            }
        ]

        # Policy categories
        policy_categories = [
            {
                'name': 'Academic Policies',
                'category_type': 'policy',
                'description': 'Academic regulations, grading policies, and educational standards'
            },
            {
                'name': 'Administrative Policies',
                'category_type': 'policy',
                'description': 'Administrative procedures, enrollment policies, and institutional guidelines'
            },
            {
                'name': 'Safety Policies',
                'category_type': 'policy',
                'description': 'Workplace safety policies, health regulations, and emergency protocols'
            },
            {
                'name': 'Student Conduct',
                'category_type': 'policy',
                'description': 'Code of conduct, disciplinary procedures, and behavioral expectations'
            },
            {
                'name': 'HR Policies',
                'category_type': 'policy',
                'description': 'Human resources policies, employment guidelines, and staff regulations'
            }
        ]

        # Create manual categories
        for category_data in manual_categories:
            category, created = DocumentCategory.objects.get_or_create(
                name=category_data['name'],
                category_type=category_data['category_type'],
                defaults={'description': category_data['description']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created manual category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Manual category already exists: {category.name}')
                )

        # Create policy categories
        for category_data in policy_categories:
            category, created = DocumentCategory.objects.get_or_create(
                name=category_data['name'],
                category_type=category_data['category_type'],
                defaults={'description': category_data['description']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created policy category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Policy category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully created document categories!')
        )
