from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Learner_Profile, ApplicantPasser
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings


@login_required
def get_learner_profile(request, profile_id):
    """Get learner profile data for the modal view"""
    try:
        profile = get_object_or_404(Learner_Profile, id=profile_id)
        
        # Get completed programs
        completed_programs = []
        if profile.user:
            # Get passed programs
            passed_programs = profile.user.passed_programs.all()
            for passed in passed_programs:
                completed_programs.append(passed.program_name)
            
            # If no passed programs, get approved programs (in progress)
            if not completed_programs:
                approved_programs = profile.user.approved_programs.all()
                for approved in approved_programs:
                    completed_programs.append(f"{approved.program.program_name} (In Progress)")
        
        # Build address string
        address_parts = []
        if profile.street:
            address_parts.append(profile.street)
        if profile.barangay_name:
            address_parts.append(profile.barangay_name)
        if profile.city_name:
            address_parts.append(profile.city_name)
        if profile.province_name:
            address_parts.append(profile.province_name)
        
        address = ", ".join(address_parts) if address_parts else "N/A"
        
        # Get classifications
        classifications = [c.name for c in profile.classifications.all()] if hasattr(profile, 'classifications') else []
        
        # Get disability types
        disability_types = [d.name for d in profile.disability_types.all()] if hasattr(profile, 'disability_types') else []
        
        # Get batch information from approved and passed programs
        batch_info = []
        if profile.user:
            # Get approved programs (in progress)
            approved_programs = profile.user.approved_programs.all()
            for approved in approved_programs:
                batch_str = f"Batch {approved.batch_number}" if approved.batch_number else "No batch"
                if approved.enrollment_year:
                    batch_str += f" ({approved.enrollment_year})"
                batch_info.append({
                    'program': approved.program.program_name if approved.program else 'N/A',
                    'batch': batch_str,
                    'status': 'In Progress'
                })
            
            # Get passed programs (completed)
            passed_programs = profile.user.passed_programs.all()
            for passed in passed_programs:
                # Try to get batch info from related approved program if available
                related_approved = profile.user.approved_programs.filter(program__program_name=passed.program_name).first()
                batch_str = "No batch"
                if related_approved:
                    batch_str = f"Batch {related_approved.batch_number}" if related_approved.batch_number else "No batch"
                    if related_approved.enrollment_year:
                        batch_str += f" ({related_approved.enrollment_year})"
                batch_info.append({
                    'program': passed.program_name,
                    'batch': batch_str,
                    'status': 'Completed'
                })
        
        profile_data = {
            'id': profile.id,
            'full_name': f"{profile.first_name} {profile.middle_name or ''} {profile.last_name}".strip(),
            'first_name': profile.first_name or 'N/A',
            'middle_name': profile.middle_name or 'N/A',
            'last_name': profile.last_name or 'N/A',
            'email': profile.email or 'N/A',
            'contact_number': profile.contact_number or 'N/A',
            'entry_date': profile.entry_date.strftime('%B %d, %Y') if profile.entry_date else None,
            'birthdate': profile.birthdate.strftime('%B %d, %Y') if profile.birthdate else None,
            'age': profile.age or 'N/A',
            'sex': profile.sex or 'N/A',
            'civil_status': profile.civil_status or 'N/A',
            'nationality': profile.nationality or 'N/A',
            'birthplace_region': profile.birthplace_regionb_name or 'N/A',
            'birthplace_province': profile.birthplace_provinceb_name or 'N/A',
            'birthplace_city': profile.birthplace_cityb_name or 'N/A',
            'address': address,
            'street': profile.street or 'N/A',
            'barangay': profile.barangay_name or 'N/A',
            'city': profile.city_name or 'N/A',
            'province': profile.province_name or 'N/A',
            'region': profile.region_name or 'N/A',
            'district': profile.district or 'N/A',
            'permanent_address': profile.permanent_address or 'N/A',
            'educational_attainment': profile.educational_attainment or 'N/A',
            'employment_status': profile.employment_status or 'N/A',
            'monthly_income': profile.monthly_income or 'N/A',
            'date_hired': profile.date_hired.strftime('%B %d, %Y') if profile.date_hired else None,
            'company_name': profile.company_name or 'N/A',
            'parent_guardian': profile.parent_guardian or 'N/A',
            'classifications': classifications,
            'other_classification': profile.other_classification or 'N/A',
            'disability_types': disability_types,
            'course_or_qualification': profile.course_or_qualification or 'N/A',
            'scholarship_package': profile.scholarship_package or 'N/A',
            'programs': completed_programs,
            'batch_info': batch_info,
            'applicant_name': profile.applicant_name or 'N/A',
            'date_accomplished': profile.date_accomplished.strftime('%B %d, %Y') if profile.date_accomplished else None,
            'id_picture': profile.id_picture.url if profile.id_picture else None,
            'username': profile.user.username if profile.user else 'N/A',
        }
        
        return JsonResponse({
            'success': True,
            'profile': profile_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_POST
def download_learner_profile(request, profile_id):
    """Generate and download HTML file for learner profile"""
    try:
        profile = get_object_or_404(Learner_Profile, id=profile_id)
        
        # Get completed programs
        completed_programs = []
        if profile.user:
            passed_programs = profile.user.passed_programs.all()
            for passed in passed_programs:
                completed_programs.append({
                    'name': passed.program_name,
                    'completion_date': passed.completion_date,
                    'final_progress': passed.final_progress
                })
            
            # If no passed programs, get approved programs
            if not completed_programs:
                approved_programs = profile.user.approved_programs.all()
                for approved in approved_programs:
                    completed_programs.append({
                        'name': approved.program.program_name,
                        'status': 'In Progress',
                        'progress': approved.progress
                    })
        
        # Build address
        address_parts = []
        if profile.street:
            address_parts.append(profile.street)
        if profile.barangay_name:
            address_parts.append(profile.barangay_name)
        if profile.city_name:
            address_parts.append(profile.city_name)
        if profile.province_name:
            address_parts.append(profile.province_name)
        
        full_name = f"{profile.first_name} {profile.middle_name or ''} {profile.last_name}".strip()
        address = ", ".join(address_parts) if address_parts else "N/A"
        
        # Simple HTML template for download
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Learner Profile - {full_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; }}
                .section {{ margin-bottom: 20px; }}
                .label {{ font-weight: bold; color: #333; }}
                .value {{ margin-left: 10px; }}
                .programs {{ margin-top: 10px; }}
                .program-item {{ margin: 5px 0; padding: 10px; background-color: #f5f5f5; border-left: 4px solid #007bff; }}
                .no-programs {{ color: #666; font-style: italic; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>LEARNER PROFILE</h1>
                <h2>{full_name}</h2>
            </div>
            
            <div class="section">
                <span class="label">Email:</span>
                <span class="value">{profile.email}</span>
            </div>
            
            <div class="section">
                <span class="label">Contact Number:</span>
                <span class="value">{profile.contact_number or 'N/A'}</span>
            </div>
            
            <div class="section">
                <span class="label">Entry Date:</span>
                <span class="value">{profile.entry_date.strftime('%B %d, %Y') if profile.entry_date else 'N/A'}</span>
            </div>
            
            <div class="section">
                <span class="label">Address:</span>
                <span class="value">{address}</span>
            </div>
            
            <div class="section">
                <span class="label">Course/Qualification:</span>
                <span class="value">{profile.course_or_qualification or 'N/A'}</span>
            </div>
            
            <div class="section">
                <div class="label">Programs:</div>
                <div class="programs">
        """
        
        if completed_programs:
            for program in completed_programs:
                if 'completion_date' in program and program['completion_date']:
                    html_content += f'<div class="program-item"><strong>{program["name"]}</strong><br>Completed on: {program["completion_date"].strftime("%B %d, %Y")}<br>Final Progress: {program["final_progress"]}%</div>'
                else:
                    html_content += f'<div class="program-item"><strong>{program["name"]}</strong><br>Status: {program.get("status", "In Progress")}<br>Progress: {program.get("progress", 0)}%</div>'
        else:
            html_content += '<div class="no-programs">No programs found</div>'
        
        html_content += """
                </div>
            </div>
            
            <div class="section" style="margin-top: 40px; text-align: center; color: #666; font-size: 12px;">
                Generated on: """ + f"{profile.entry_date.strftime('%B %d, %Y') if profile.entry_date else 'N/A'}" + """
            </div>
        </body>
        </html>
        """
        
        # Return HTML file for download
        response = HttpResponse(html_content, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="learner_profile_{profile.id}_{full_name.replace(" ", "_")}.html"'
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def download_profile_pdf(request):
    """Generate and download PDF of user's profile based on registration_f1.html format"""
    try:
        # Get the current user's profile
        profile = get_object_or_404(Learner_Profile, user=request.user)
        
        # Create a BytesIO buffer to receive PDF data
        buffer = BytesIO()
        
        # Create the PDF object using A4 size
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                rightMargin=0.5*inch, leftMargin=0.5*inch,
                                topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a202c'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#1a202c')
        )
        
        # Header
        header_data = [
            [Paragraph('<b>Technical Education and Skills Development Authority</b>', normal_style)],
            [Paragraph('<i>Pangasiwaan sa Edukasyong Teknikal at Pagpapaunlad ng Kasanayan</i>', normal_style)],
            [Paragraph('MIS 03 – 01 (ver. 2020)', normal_style)]
        ]
        header_table = Table(header_data, colWidths=[7*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 12))
        
        # Title
        elements.append(Paragraph("LEARNER'S PROFILE FORM", title_style))
        elements.append(Spacer(1, 20))
        
        # Section 1: T2MIS Auto Generated
        elements.append(Paragraph("1. T2MIS Auto Generated", heading_style))
        section1_data = [
            ['1.1. Unique Learner Identifier (ULI) Number:', 'Auto-generated'],
            ['1.2. Entry Date:', profile.entry_date.strftime('%B %d, %Y') if profile.entry_date else 'N/A']
        ]
        section1_table = Table(section1_data, colWidths=[3.5*inch, 3.5*inch])
        section1_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(section1_table)
        elements.append(Spacer(1, 15))
        
        # Section 2: Learner/Manpower Profile
        elements.append(Paragraph("2. Learner/Manpower Profile", heading_style))
        
        # Name
        section2_name_data = [
            ['2.1. Name:'],
            ['Last Name', 'First Name', 'Middle Name', 'Extension'],
            [profile.last_name or '', profile.first_name or '', profile.middle_name or '', profile.extension_name or '']
        ]
        section2_name_table = Table(section2_name_data, colWidths=[1.75*inch, 1.75*inch, 1.75*inch, 1.75*inch])
        section2_name_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('SPAN', (0, 0), (-1, 0)),
            ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(section2_name_table)
        elements.append(Spacer(1, 10))
        
        # Address
        address_parts = []
        if profile.street:
            address_parts.append(f"Street: {profile.street}")
        if profile.barangay_name:
            address_parts.append(f"Barangay: {profile.barangay_name}")
        if profile.city_name:
            address_parts.append(f"City: {profile.city_name}")
        if profile.province_name:
            address_parts.append(f"Province: {profile.province_name}")
        if profile.region_name:
            address_parts.append(f"Region: {profile.region_name}")
        
        address_text = ', '.join(address_parts) if address_parts else 'N/A'
        
        section2_address_data = [
            ['2.2. Complete Permanent Mailing Address:', address_text]
        ]
        section2_address_table = Table(section2_address_data, colWidths=[2.5*inch, 4.5*inch])
        section2_address_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(section2_address_table)
        elements.append(Spacer(1, 10))
        
        # Contact Information
        section2_contact_data = [
            ['Email Address:', profile.email or 'N/A'],
            ['Contact Number:', profile.contact_number or 'N/A'],
            ['Nationality:', profile.nationality or 'N/A'],
            ['Skills:', profile.skills or 'N/A']
        ]
        section2_contact_table = Table(section2_contact_data, colWidths=[2*inch, 5*inch])
        section2_contact_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(section2_contact_table)
        elements.append(Spacer(1, 15))
        
        # Section 3: Personal Information
        elements.append(Paragraph("3. Personal Information", heading_style))
        
        section3_data = [
            ['3.1. Sex:', profile.sex or 'N/A'],
            ['3.2. Civil Status:', profile.civil_status or 'N/A'],
            ['3.3. Employment Status:', profile.employment_status or 'N/A'],
        ]
        
        if profile.employment_status == 'Employed':
            section3_data.extend([
                ['Monthly Income:', profile.monthly_income or 'N/A'],
                ['Date Hired:', profile.date_hired.strftime('%B %d, %Y') if profile.date_hired else 'N/A'],
                ['Company Name:', profile.company_name or 'N/A']
            ])
        
        section3_table = Table(section3_data, colWidths=[2.5*inch, 4.5*inch])
        section3_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(section3_table)
        elements.append(Spacer(1, 10))
        
        # Birthdate
        birthdate_str = 'N/A'
        if hasattr(profile, 'birthdate') and profile.birthdate:
            birthdate_str = profile.birthdate.strftime('%B %d, %Y')
        
        section3_birth_data = [
            ['3.4. Birthdate:', birthdate_str],
            ['Age:', str(profile.age) if profile.age else 'N/A']
        ]
        section3_birth_table = Table(section3_birth_data, colWidths=[2.5*inch, 4.5*inch])
        section3_birth_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(section3_birth_table)
        elements.append(Spacer(1, 10))
        
        # Birthplace
        birthplace_parts = []
        if hasattr(profile, 'birthplace_cityb_name') and profile.birthplace_cityb_name:
            birthplace_parts.append(profile.birthplace_cityb_name)
        if hasattr(profile, 'birthplace_provinceb_name') and profile.birthplace_provinceb_name:
            birthplace_parts.append(profile.birthplace_provinceb_name)
        if hasattr(profile, 'birthplace_regionb_name') and profile.birthplace_regionb_name:
            birthplace_parts.append(profile.birthplace_regionb_name)
        
        birthplace_text = ', '.join(birthplace_parts) if birthplace_parts else 'N/A'
        
        section3_birthplace_data = [
            ['3.5. Birthplace:', birthplace_text],
            ['3.7. Parent/Guardian:', profile.parent_guardian or 'N/A']
        ]
        section3_birthplace_table = Table(section3_birthplace_data, colWidths=[2.5*inch, 4.5*inch])
        section3_birthplace_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(section3_birthplace_table)
        elements.append(Spacer(1, 15))
        
        # Section 4: Educational Attainment
        elements.append(Paragraph("4. Educational Attainment", heading_style))
        
        section4_data = [
            ['Educational Attainment:', profile.educational_attainment or 'N/A'],
            ['Course/Qualification:', profile.course_or_qualification or 'N/A'],
            ['Scholarship Package:', profile.scholarship_package or 'N/A']
        ]
        section4_table = Table(section4_data, colWidths=[2.5*inch, 4.5*inch])
        section4_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(section4_table)
        elements.append(Spacer(1, 20))
        
        # Footer
        footer_data = [
            [Paragraph(f'<i>Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</i>', normal_style)]
        ]
        footer_table = Table(footer_data, colWidths=[7*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(Spacer(1, 30))
        elements.append(footer_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and return it as a response
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create the HttpResponse object with the appropriate PDF headers
        response = HttpResponse(content_type='application/pdf')
        full_name = f"{profile.first_name}_{profile.last_name}".replace(" ", "_")
        response['Content-Disposition'] = f'attachment; filename="Learner_Profile_{full_name}.pdf"'
        response.write(pdf)
        
        return response
        
    except Learner_Profile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Profile not found. Please complete your profile first.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error generating PDF: {str(e)}'
        }, status=500)


@login_required
def registration_form_pdf(request, profile_id):
    """Render a registration-form styled page that auto-generates a PDF via html2pdf.js
    This uses a dedicated template which mirrors registration_form.html but binds fields to the
    Learner_Profile instance and triggers client-side PDF download.
    """
    try:
        profile = get_object_or_404(Learner_Profile, id=profile_id)

        # Build address text pieces for convenience
        address_parts = []
        if profile.street:
            address_parts.append(profile.street)
        if profile.barangay_name:
            address_parts.append(profile.barangay_name)
        if profile.city_name:
            address_parts.append(profile.city_name)
        if profile.province_name:
            address_parts.append(profile.province_name)
        if profile.region_name:
            address_parts.append(profile.region_name)
        address_text = ", ".join(address_parts)

        context = {
            'profile': profile,
            'full_name': f"{profile.first_name} {profile.middle_name or ''} {profile.last_name}".strip(),
            'address_text': address_text,
            'today_str': datetime.now().strftime('%B %d, %Y %I:%M %p')
        }

        from django.shortcuts import render
        return render(request, 'registration_form_pdf.html', context)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error preparing registration form PDF: {str(e)}'
        }, status=500)


@login_required
def download_certificate_pdf(request):
    """Generate and download a simple Certificate of Completion PDF for users who passed a program."""
    try:
        # Ensure the user is a passer
        passer = ApplicantPasser.objects.filter(applicant=request.user).select_related('program').first()
        if not passer:
            return JsonResponse({
                'success': False,
                'error': 'Certificate is available only after you complete a program.'
            }, status=403)

        # Get user's profile
        profile = get_object_or_404(Learner_Profile, user=request.user)

        # Prepare PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CertTitle', parent=styles['Heading1'], fontSize=22, alignment=TA_CENTER,
            textColor=colors.HexColor('#1e3a8a'), spaceAfter=14
        )
        subtitle_style = ParagraphStyle(
            'CertSub', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER,
            textColor=colors.HexColor('#6b7280'), spaceAfter=10
        )
        name_style = ParagraphStyle(
            'NameStyle', parent=styles['Heading1'], fontSize=20, alignment=TA_CENTER,
            textColor=colors.HexColor('#0f172a'), spaceAfter=8
        )
        body_style = ParagraphStyle(
            'BodyStyle', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER,
            textColor=colors.HexColor('#374151'), leading=16, spaceAfter=12
        )
        foot_label_style = ParagraphStyle(
            'FootLbl', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER,
            textColor=colors.HexColor('#6b7280')
        )
        foot_value_style = ParagraphStyle(
            'FootVal', parent=styles['Heading3'], fontSize=11, alignment=TA_CENTER,
            textColor=colors.HexColor('#1f2937')
        )

        # Header
        elements.append(Paragraph('Lucena Manpower Skill Training Center', title_style))
        elements.append(Paragraph('Dalubhasaan ng Lungsod ng Lucena', subtitle_style))
        elements.append(Spacer(1, 14))

        # Certificate Title
        elements.append(Paragraph('Certificate of Completion', title_style))
        elements.append(Spacer(1, 6))

        # Body
        elements.append(Paragraph('This is to certify that', body_style))
        full_name = f"{profile.first_name} {profile.middle_name or ''} {profile.last_name}".strip()
        elements.append(Paragraph(full_name, name_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph('has successfully completed the requirements for', body_style))
        program_name = passer.program.program_name if passer.program else passer.program_name
        elements.append(Paragraph(program_name, ParagraphStyle('Program', parent=body_style, fontSize=13, textColor=colors.HexColor('#1e3a8a'))))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph('and has demonstrated proficiency in the required skills and competencies.', body_style))
        elements.append(Spacer(1, 18))

        # Footer details (3 columns style)
        issued_date = (profile.date_accomplished.strftime('%B %d, %Y') if getattr(profile, 'date_accomplished', None)
                       else passer.completion_date.strftime('%B %d, %Y') if passer.completion_date else datetime.now().strftime('%B %d, %Y'))

        footer_table = Table([
            [
                Paragraph('<br/><br/><br/>______________________________', foot_label_style),
                Paragraph('Date Issued:<br/>' + issued_date, foot_value_style),
                Paragraph('<br/><br/><br/>______________________________', foot_label_style),
            ],
            [
                Paragraph('Trainer/Coordinator', foot_label_style),
                Paragraph('', foot_label_style),
                Paragraph('Recipient Signature', foot_label_style),
            ]
        ], colWidths=[2.5*inch, 2.0*inch, 2.5*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(Spacer(1, 20))
        elements.append(footer_table)

        # Build and return
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Certificate_{full_name.replace(" ", "_")}.pdf"'
        response.write(pdf)
        return response

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error generating certificate: {str(e)}'
        }, status=500)
