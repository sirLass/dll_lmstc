from django import forms
from django.contrib.auth import get_user_model
from .models import Learner_Profile, Training

# Get the custom user model
User = get_user_model()  # This will get your Applicant.Applicant model

class LearnerProfileForm(forms.ModelForm):
    class Meta:
        model = Learner_Profile  # Use the correct model name with underscore
        fields = '__all__'  # use this if you want to include ALL fields in the form
        widgets = {
            'entry_date': forms.DateInput(attrs={'type': 'date'}),
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
            'date_hired': forms.DateInput(attrs={'type': 'date'}),
        }

class TrainingForm(forms.ModelForm):
    task_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'time'
        })
    )
    
    end_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'time'
        })
    )
    
    # ✅ ADD END_DATE FIELD
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        })
    )
    
    CATEGORY_CHOICES = [
        ('activity', 'Activity'),
        ('examination', 'Examination'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
    ]
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'rows': 3,
            'placeholder': 'Enter task description'
        })
    )
    
    class Meta:
        model = Training
        # INCLUDE 'end_date' AND BATCH CYCLE FIELDS IN THE FIELDS LIST
        fields = ['program_name', 'start_date', 'end_date', 'task_time', 'end_time', 'room_lab', 'trainer', 'category', 'description', 'batch_number', 'semester', 'enrollment_year']
        widgets = {
            'program_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter program name'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            # ✅ ADD END_DATE WIDGET
            'end_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'trainer': forms.HiddenInput(),  # Hide trainer field since it's set automatically
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ✅ SET UP ROOM/LAB CHOICES
        ROOM_CHOICES = [
            ('', 'Select Room/Lab'),
            ('Lab A', 'Lab A'),
            ('Lab B', 'Lab B'),
            ('Lab C', 'Lab C'),
            ('Conference Room', 'Conference Room'),
            ('Training Room 1', 'Training Room 1'),
            ('Training Room 2', 'Training Room 2'),
            ('Workshop Area', 'Workshop Area'),
            ('Computer Lab', 'Computer Lab'),
        ]
        
        self.fields['room_lab'] = forms.ChoiceField(
            choices=ROOM_CHOICES,
            required=True,
            widget=forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            })
        )

class EmployerSignUpForm(forms.Form):
    company_name = forms.CharField(max_length=255)
    contact_person = forms.CharField(max_length=255)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    terms = forms.BooleanField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")
        return password