from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import ApprovedApplicant, Learner_Profile
# import pandas as pd  # Temporarily commented out due to missing dependency
import json
import os

# OCR Excel Processing Views
@csrf_exempt
@require_POST
def process_excel_ocr(request):
    """Process uploaded Excel file for OCR"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No file uploaded'})
        
        file = request.FILES['file']
        if not file.name.endswith(('.xlsx', '.xls')):
            return JsonResponse({'success': False, 'message': 'Please upload an Excel file'})
        
        # Excel processing temporarily disabled due to missing pandas dependency
        return JsonResponse({
            'success': False,
            'message': 'Excel processing is temporarily unavailable. Please install pandas dependency first.'
        })
        
        return JsonResponse({
            'success': True,
            'extracted_data': data,
            'columns': columns,
            'total_rows': len(data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing Excel file: {str(e)}'
        })

@csrf_exempt
@require_POST
def process_default_excel(request):
    """Process the default 2024.xlsx file"""
    try:
        # Path to the default Excel file
        file_path = os.path.join(settings.BASE_DIR, 'DLL_LMSTC', 'Applicant', 'static', 'data', '2024.xlsx')
        
        if not os.path.exists(file_path):
            return JsonResponse({'success': False, 'message': '2024.xlsx file not found'})
        
        # Excel processing temporarily disabled due to missing pandas dependency
        return JsonResponse({
            'success': False,
            'message': 'Excel processing is temporarily unavailable. Please install pandas dependency first.'
        })
        
        return JsonResponse({
            'success': True,
            'extracted_data': data,
            'columns': columns,
            'total_rows': len(data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing 2024.xlsx: {str(e)}'
        })

@csrf_exempt
@require_POST
def save_excel_data(request):
    """Save extracted Excel data to ApprovedApplicant and Learner_Profile models"""
    try:
        data = json.loads(request.body)
        extracted_data = data.get('data', [])
        columns = data.get('columns', [])
        
        if not extracted_data:
            return JsonResponse({'success': False, 'message': 'No data to save'})
        
        # Get model fields for mapping
        approved_applicant_fields = [field.name for field in ApprovedApplicant._meta.get_fields()]
        learner_profile_fields = [field.name for field in Learner_Profile._meta.get_fields()]
        
        created_count = 0
        updated_count = 0
        
        for row in extracted_data:
            try:
                # Map columns to model fields
                approved_data = {}
                learner_data = {}
                
                for col in columns:
                    col_lower = col.lower().replace(' ', '_').replace('-', '_')
                    
                    # Map to ApprovedApplicant fields
                    if col_lower in approved_applicant_fields or col in approved_applicant_fields:
                        field_name = col_lower if col_lower in approved_applicant_fields else col
                        if field_name not in ['id', 'applicant', 'program']:  # Skip foreign keys and id
                            approved_data[field_name] = row.get(col, '')
                    
                    # Map to Learner_Profile fields
                    if col_lower in learner_profile_fields or col in learner_profile_fields:
                        field_name = col_lower if col_lower in learner_profile_fields else col
                        if field_name not in ['id', 'user']:  # Skip foreign keys and id
                            learner_data[field_name] = row.get(col, '')
                
                # Handle specific field mappings based on common Excel column names
                field_mappings = {
                    'name': 'first_name',
                    'full_name': 'first_name',
                    'firstname': 'first_name',
                    'lastname': 'last_name',
                    'surname': 'last_name',
                    'middlename': 'middle_name',
                    'middle': 'middle_name',
                    'phone': 'contact_number',
                    'mobile': 'contact_number',
                    'contact': 'contact_number',
                    'address': 'street',
                    'gender': 'sex',
                    'birthday': 'birthdate',
                    'birth_date': 'birthdate',
                    'dob': 'birthdate',
                }
                
                # Apply field mappings to learner_data
                for excel_col, model_field in field_mappings.items():
                    for col in columns:
                        if col.lower().replace(' ', '_').replace('-', '_') == excel_col:
                            if model_field in learner_profile_fields and row.get(col):
                                learner_data[model_field] = row.get(col)
                
                # Try to find existing records or create new ones
                # For this example, we'll create Learner_Profile records
                if learner_data:
                    # Check if we have enough data to create a meaningful record
                    if learner_data.get('first_name') or learner_data.get('last_name') or learner_data.get('email'):
                        # Try to find existing record by email or name
                        existing_profile = None
                        if learner_data.get('email'):
                            try:
                                existing_profile = Learner_Profile.objects.get(email=learner_data['email'])
                            except Learner_Profile.DoesNotExist:
                                pass
                        
                        if existing_profile:
                            # Update existing record
                            for field, value in learner_data.items():
                                if value and hasattr(existing_profile, field):
                                    setattr(existing_profile, field, value)
                            existing_profile.save()
                            updated_count += 1
                        else:
                            # Create new record
                            # Set required fields with defaults if not provided
                            if not learner_data.get('last_name'):
                                learner_data['last_name'] = 'Unknown'
                            if not learner_data.get('first_name'):
                                learner_data['first_name'] = 'Unknown'
                            if not learner_data.get('email'):
                                learner_data['email'] = f'unknown_{created_count}@example.com'
                            if not learner_data.get('region'):
                                learner_data['region'] = 'Unknown'
                            if not learner_data.get('province'):
                                learner_data['province'] = 'Unknown'
                            if not learner_data.get('city'):
                                learner_data['city'] = 'Unknown'
                            if not learner_data.get('barangay'):
                                learner_data['barangay'] = 'Unknown'
                            if not learner_data.get('street'):
                                learner_data['street'] = 'Unknown'
                            
                            Learner_Profile.objects.create(**learner_data)
                            created_count += 1
                            
            except Exception as row_error:
                print(f"Error processing row: {row_error}")
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Data saved successfully. {created_count} records created, {updated_count} records updated.',
            'created_count': created_count,
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error saving data: {str(e)}'
        })
