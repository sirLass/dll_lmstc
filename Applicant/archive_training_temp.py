@require_POST
def archive_training(request):
    """Archive a training session by moving it to the ArchivedTraining model"""
    try:
        training_id = request.POST.get('training_id')
        
        if not training_id:
            return JsonResponse({'success': False, 'message': 'Training ID is required'})
        
        # Get the training session
        training = get_object_or_404(Training, id=training_id)
        
        # Check if user has permission to archive (should be staff or the trainer)
        if not (request.user.is_staff or training.trainer == request.user):
            return JsonResponse({'success': False, 'message': 'You do not have permission to archive this training'})
        
        # Create archived training record
        archived_training = ArchivedTraining.objects.create(
            program_name=training.program_name,
            start_date=training.start_date,
            end_date=training.end_date,
            task_time=training.task_time,
            end_time=training.end_time,
            room_lab=training.room_lab,
            trainer=training.trainer,
            category=training.category,
            description=training.description,
            archived_by=request.user,
            archive_reason=request.POST.get('reason', 'Archived by trainer'),
            original_created_at=training.created_at,
            original_updated_at=training.updated_at
        )
        
        # Delete the original training session
        training.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'Training session archived successfully',
            'archived_id': archived_training.id
        })
        
    except Training.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Training session not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error archiving training: {str(e)}'})
