from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import TrainerProfile, Programs
import json


@staff_member_required
@require_http_methods(["GET"])
def get_trainer_programs(request, trainer_id):
    """Get all programs assigned to a trainer"""
    try:
        trainer = TrainerProfile.objects.prefetch_related('programs').get(id=trainer_id)
        assigned_programs = list(trainer.programs.values('id', 'program_name'))
        all_programs = list(Programs.objects.values('id', 'program_name'))
        
        # Get all programs that are assigned to ANY trainer (excluding current trainer)
        assigned_to_others = TrainerProfile.objects.exclude(id=trainer_id).prefetch_related('programs')
        programs_in_use = set()
        for other_trainer in assigned_to_others:
            programs_in_use.update(other_trainer.programs.values_list('id', flat=True))
        
        return JsonResponse({
            'success': True,
            'assigned_programs': assigned_programs,
            'all_programs': all_programs,
            'programs_in_use': list(programs_in_use),  # Programs assigned to other trainers
            'trainer_name': f"{trainer.user.first_name} {trainer.user.last_name}" if trainer.user.first_name else trainer.user.username
        })
    except TrainerProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Trainer not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def assign_program_to_trainer(request, trainer_id):
    """Assign a program to a trainer"""
    try:
        data = json.loads(request.body)
        program_id = data.get('program_id')
        
        if not program_id:
            return JsonResponse({'success': False, 'message': 'Program ID is required'}, status=400)
        
        trainer = TrainerProfile.objects.get(id=trainer_id)
        program = Programs.objects.get(id=program_id)
        
        # Check if already assigned
        if trainer.programs.filter(id=program_id).exists():
            return JsonResponse({'success': False, 'message': 'Program already assigned to this trainer'}, status=400)
        
        trainer.programs.add(program)
        
        # Update legacy program field if this is the first program
        if not trainer.program:
            trainer.program = program
            trainer.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Program "{program.program_name}" assigned successfully'
        })
    except TrainerProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Trainer not found'}, status=404)
    except Programs.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Program not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def unassign_program_from_trainer(request, trainer_id):
    """Unassign a program from a trainer"""
    try:
        data = json.loads(request.body)
        program_id = data.get('program_id')
        
        if not program_id:
            return JsonResponse({'success': False, 'message': 'Program ID is required'}, status=400)
        
        trainer = TrainerProfile.objects.get(id=trainer_id)
        program = Programs.objects.get(id=program_id)
        
        # Check if program is assigned
        if not trainer.programs.filter(id=program_id).exists():
            return JsonResponse({'success': False, 'message': 'Program not assigned to this trainer'}, status=400)
        
        trainer.programs.remove(program)
        
        # Update legacy program field if we removed it
        if trainer.program and trainer.program.id == int(program_id):
            # Set to the first remaining program or None
            remaining_programs = trainer.programs.first()
            trainer.program = remaining_programs
            trainer.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Program "{program.program_name}" unassigned successfully'
        })
    except TrainerProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Trainer not found'}, status=404)
    except Programs.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Program not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def delete_trainer_account(request, trainer_id):
    """Delete a trainer account completely (both TrainerProfile and User)"""
    try:
        trainer = TrainerProfile.objects.select_related('user').get(id=trainer_id)
        user = trainer.user
        username = user.username
        
        # Delete the TrainerProfile (this will cascade delete related objects)
        trainer.delete()
        
        # Delete the User account
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Trainer account "{username}" has been deleted successfully'
        })
    except TrainerProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Trainer not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
