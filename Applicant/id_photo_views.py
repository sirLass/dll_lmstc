from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Learner_Profile
import os

@login_required
@csrf_exempt
@require_POST
def update_id_photo(request):
    """Handle ID photo upload/update from dashboard"""
    try:
        # Get the user's profile
        profile = get_object_or_404(Learner_Profile, user=request.user)
        
        # Check if a file was uploaded
        if 'id_picture' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No file uploaded'
            })
        
        id_photo = request.FILES['id_picture']
        
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        file_ext = os.path.splitext(id_photo.name)[1].lower()
        
        if file_ext not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': 'Invalid file type. Only JPG, PNG, and GIF are allowed.'
            })
        
        # Validate file size (max 5MB)
        if id_photo.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'File size too large. Maximum size is 5MB.'
            })
        
        # Delete old photo if exists
        if profile.id_picture:
            try:
                if os.path.isfile(profile.id_picture.path):
                    os.remove(profile.id_picture.path)
            except:
                pass  # Continue even if deletion fails
        
        # Save new photo
        profile.id_picture = id_photo
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'ID Photo updated successfully!',
            'photo_url': profile.id_picture.url
        })
        
    except Learner_Profile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Profile not found. Please create your profile first.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error updating ID photo: {str(e)}'
        })


@login_required
def view_ticket(request, ticket_id):
    """View details of a specific support ticket"""
    from .models import SupportTicket, TicketResponse
    
    ticket = get_object_or_404(SupportTicket, id=ticket_id, created_by=request.user)
    responses = TicketResponse.objects.filter(ticket=ticket).order_by('created_at')
    
    context = {
        'ticket': ticket,
        'responses': responses,
        'username': request.user.username,
    }
    
    return render(request, 'ticket_detail.html', context)
