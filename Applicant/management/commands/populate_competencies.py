from django.core.management.base import BaseCommand
from Applicant.models import Programs

class Command(BaseCommand):
    help = 'Populate competencies data for programs with actual data from templates'

    def handle(self, *args, **options):
        # Define competencies data for each program based on existing templates
        programs_data = {
            'Auto Electrical Assembly NCII': {
                'basic_competencies': [
                    'Participate in Workplace Communication',
                    'Work in a Team Environment',
                    'Practice Career Professionalism',
                    'Practice Occupational Health and Safety Procedures'
                ],
                'common_competencies': [
                    'Perform Mensuration and Calculation',
                    'Read, Interpret and Apply Engineering Drawings',
                    'Move and Position a Vehicle',
                    'Apply Appropriate Sealant/Adhesive',
                    'Perform Shop Maintenance'
                ],
                'core_competencies': [
                    'Install/Fit Out Electrical Parts to Engine Assembly',
                    'Install/Fit Out Electrical Parts and Electronic Units to Body Interior Compartment',
                    'Install/Fit Out Electrical Parts and Electronic Units to Dash Instrument Panel',
                    'Install/Fit Out Electrical Parts to Exterior and Engine Compartment',
                    'Install/Fit Out Audio and Video Systems',
                    'Perform Headlight Focus Aiming Operations'
                ],
                'job_opportunities': [
                    'Automotive Electrical Assembly Technician'
                ]
            },
            'Auto Mechanical Assembly NCII': {
                'basic_competencies': [
                    'Participate in Workplace Communication',
                    'Work in Team Environment',
                    'Practice Career Professionalism',
                    'Practice Occupational Health and Safety Procedures'
                ],
                'common_competencies': [
                    'Perform Mensuration and Calculation',
                    'Read, Interpret and Apply Engineering Drawings',
                    'Move and Position Vehicle',
                    'Apply Appropriate Sealant/Adhesive',
                    'Perform Shop Maintenance'
                ],
                'core_competencies': [
                    'Assemble Mechanical Assemblies using Jigs/Fixtures',
                    'Mount/Install Brake and Fuel Systems',
                    'Mount/Install Power Drive System',
                    'Mount/Install Suspension Drive Train',
                    'Install/Fit out Trim Parts and Assemblies',
                    'Perform Final Engine Run',
                    'Perform Wheel Alignment Operations'
                ],
                'job_opportunities': [
                    'Automotive Mechanical Assembly Technician'
                ]
            },
            'Bread and Pastry Production NC II': {
                'basic_competencies': [
                    'Participate in workplace communication',
                    'Work in team environment',
                    'Practice career professionalism',
                    'Practice occupational health and safety procedures'
                ],
                'common_competencies': [
                    'Develop and update industry knowledge',
                    'Observe workplace hygiene procedures',
                    'Perform computer operations',
                    'Perform workplace and safety practices',
                    'Provide effective customer service'
                ],
                'core_competencies': [
                    'Prepare and produce bakery products',
                    'Prepare and produce pastry products',
                    'Prepare and present pastries, cookies, and cakes',
                    'Prepare and display petits fours',
                    'Present desserts'
                ],
                'job_opportunities': [
                    'Commis - Pastry',
                    'Baker'
                ]
            },
            'Dressmaking NC II': {
                'basic_competencies': [
                    'Participate in workplace communication',
                    'Work in a team environment',
                    'Practice career professionalism',
                    'Practice occupational health and safety procedures'
                ],
                'common_competencies': [
                    'Carry out measurements and calculation',
                    'Set up and operate machine/s',
                    'Perform basic maintenance',
                    'Apply quality standards'
                ],
                'core_competencies': [
                    'Draft and cut pattern of casual apparel',
                    'Prepare and cut materials of casual apparel',
                    'Sew casual apparel',
                    'Apply finishing touches on casual apparel'
                ],
                'job_opportunities': [
                    'Dressmaker',
                    'Garment Sewer'
                ]
            },
            'Electrical Installation and Maintenance NC II': {
                'basic_competencies': [
                    'Participate in workplace communication',
                    'Work in team environment',
                    'Practice career professionalism',
                    'Practice occupational health and safety procedures'
                ],
                'common_competencies': [
                    'Use hand tools',
                    'Perform mensuration and calculation',
                    'Prepare and interpret technical drawing',
                    'Apply quality standards',
                    'Terminate and connect electrical wiring and electronic circuits'
                ],
                'core_competencies': [
                    'Perform roughing-in activities, wiring and cabling works for single-phase distribution, power, lighting, and auxiliary systems',
                    'Install electrical protective devices for distribution, power, lighting, auxiliary, lightning protection, and grounding systems',
                    'Install wiring devices of floor and wall-mounted outlets, lighting fixtures/switches, and auxiliary outlets'
                ],
                'job_opportunities': [
                    'Building-Wiring Electrician',
                    'Residential/Commercial-Wiring Electrician',
                    'Maintenance Electrician'
                ]
            },
            'Electronic Products Assembly and Service NC II': {
                'basic_competencies': [
                    'Participate in workplace communication',
                    'Work in team environment',
                    'Practice career professionalism',
                    'Practice occupational health and safety procedures'
                ],
                'common_competencies': [
                    'Apply quality standards',
                    'Perform computer operations',
                    'Perform mensuration and calculation',
                    'Prepare and interpret technical drawing',
                    'Use hand tools',
                    'Terminate and connect electrical wiring and electronic circuits',
                    'Test electronic components'
                ],
                'core_competencies': [
                    'Assemble electronic products',
                    'Service consumer electronic products and systems',
                    'Service industrial electronic modules, products, and systems'
                ],
                'job_opportunities': [
                    'Electronic Products Assembler',
                    'Domestic Appliance Service Technician',
                    'Audio-Video Service Technician',
                    'Industrial Electronic Technician',
                    'Electronic Production Line Assembler',
                    'Factory Production Worker'
                ]
            },
            'Hairdressing NC II': {
                'basic_competencies': [
                    'Participate in workplace communication',
                    'Work in team environment',
                    'Practice career professionalism',
                    'Practice occupational health and safety procedures'
                ],
                'common_competencies': [
                    'Maintain an effective relationship with clients/customers',
                    'Manage own performance',
                    'Apply quality standards',
                    'Maintain a safe, clean, and efficient environment'
                ],
                'core_competencies': [
                    'Perform pre- and post- hair care activities',
                    'Perform hair and scalp treatment',
                    'Perform basic hair perming',
                    'Perform basic hair coloring',
                    'Perform basic haircutting',
                    'Perform hair bleaching',
                    'Perform hair straightening',
                    'Apply basic make-up'
                ],
                'job_opportunities': [
                    'Junior Assistant',
                    'Colorist',
                    'Permist',
                    'Make-up Artist',
                    'Haircutter',
                    'Hairstylist'
                ]
            },
            'Massage Therapy NC II': {
                'basic_competencies': [
                    'Maintain effective relationship with clients',
                    'Respond effectively to difficult/challenging behavior',
                    'Apply basic first aid',
                    'Maintain high standard of client services'
                ],
                'common_competencies': [
                    'Prepare materials and tools',
                    'Interpret technical drawings',
                    'Observe procedures, specifications and manuals of instructions',
                    'Perform mensurations and calculations',
                    'Perform basic benchworks',
                    'Perform basic electrical works',
                    'Maintain tools and equipment',
                    'Perform housekeeping and safety practices',
                    'Document work accomplished'
                ],
                'core_competencies': [
                    'Develop massage practice',
                    'Perform client consultation',
                    'Perform body massage',
                    'Maintain and organize tools, equipment, supplies and work area'
                ],
                'job_opportunities': [
                    'Massage Therapist'
                ]
            },
            'RAC SERVICING (DomRAC) NC II': {
                'basic_competencies': [
                    'Participate in workplace communication',
                    'Work in team environment',
                    'Practice career professionalism',
                    'Practice occupational health and safety procedures'
                ],
                'common_competencies': [
                    'Apply quality standards',
                    'Perform computer operations',
                    'Perform mensuration and calculation',
                    'Use hand tools',
                    'Apply safety practices'
                ],
                'core_competencies': [
                    'Service domestic refrigeration systems',
                    'Service domestic air conditioning systems',
                    'Diagnose and repair RAC systems'
                ],
                'job_opportunities': [
                    'RAC Technician',
                    'Appliance Service Technician'
                ]
            },
            'Shielded Metal Arc Welding NC II': {
                'basic_competencies': [
                    'Receive and respond to workplace communication',
                    'Work in a team environment',
                    'Practice career professionalism',
                    'Practice occupational health and safety procedures'
                ],
                'common_competencies': [
                    'Apply safety practices',
                    'Interpret drawings and sketches',
                    'Perform industry calculations',
                    'Contribute to quality system',
                    'Use hand tools',
                    'Prepare weld materials',
                    'Set up welding equipment',
                    'Fit-up weld materials',
                    'Repair welds'
                ],
                'core_competencies': [
                    'Weld carbon steel plates and pipes using SMAW'
                ],
                'job_opportunities': [
                    'Shielded Metal Arc Welder'
                ]
            }
        }

        # Update or create programs with competencies
        for program_name, competencies in programs_data.items():
            program, created = Programs.objects.get_or_create(
                program_name=program_name,
                defaults={
                    'program_detail': f'{program_name} training program',
                    'program_sched': 'TBD',
                    'program_trainor': 'TBD',
                    'program_competencies': competencies
                }
            )
            
            if not created:
                # Update existing program with new competencies
                program.program_competencies = competencies
                program.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated competencies for "{program_name}"')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Created program "{program_name}" with competencies')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated all program competencies with actual template data!')
        )
