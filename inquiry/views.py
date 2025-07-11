from django.shortcuts import render, redirect
from .models import Inquiry, Patient, Claim
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

@csrf_exempt
def index(request):
    if request.method == 'POST':
        client_name = request.POST.get('clientName')
        claims_type = request.POST.get('claimsType')
        provider_name = request.POST.get('providerName')
        tax_id = request.POST.get('taxId')
        npi = request.POST.get('npi')

        inquiry = Inquiry.objects.create(
            client_name=client_name,
            claims_type=claims_type,
            provider_name=provider_name,
            tax_id=tax_id,
            npi=npi
        )

        # Patients data
        patient_count = 1
        patients_info = []
        import datetime
        while True:
            patient_name = request.POST.get(f'patient{patient_count}Name')
            patient_dob = request.POST.get(f'patient{patient_count}DOB')
            if not patient_name or not patient_dob:
                break
            # Convert DOB from MM/DD/YYYY to YYYY-MM-DD
            try:
                dob_obj = datetime.datetime.strptime(patient_dob, '%m-%d-%Y')
                patient_dob_formatted = dob_obj.strftime('%Y-%m-%d')
            except ValueError:
                patient_dob_formatted = patient_dob  # fallback if format is unexpected
            patient = Patient.objects.create(
                inquiry=inquiry,
                name=patient_name,
                dob=patient_dob_formatted
            )
            claims_info = []
            # Claims for patient
            for i in range(1, 4):
                dos = request.POST.get(f'p{patient_count}dos{i}')
                amount = request.POST.get(f'p{patient_count}amount{i}')
                if dos or amount:
                    Claim.objects.create(
                        patient=patient,
                        date_of_service=dos if dos else '',
                        amount=amount if amount else 0
                    )
                    claims_info.append(f"DOS: {dos if dos else 'N/A'}, Amount: {amount if amount else '0'}")
            patients_info.append({
                'name': patient_name,
                'dob': patient_dob,
                'claims': claims_info
            })
            patient_count += 1

        # Prepare email content
        admin_email = 'akshay.kumar@onesmarter.com'  
        subject = 'New Missing Claims Inquiry Submitted'
        message_lines = [
            "New Missing Claims Inquiry Submitted",
            "-----------------------------------",
            "",
            "Client Information:",
            f"  Client Name: {client_name}",
            f"  Claims Type: {claims_type}",
            f"  Provider Name: {provider_name}",
            f"  Tax ID: {tax_id}",
            f"  NPI: {npi}",
            "",
            "Patients and Claims Information:",
            "--------------------------------"
        ]
        for idx, p in enumerate(patients_info, start=1):
            message_lines.append(f"Patient {idx}:")
            message_lines.append(f"  Name: {p['name']}")
            message_lines.append(f"  Date of Birth: {p['dob']}")
            if p['claims']:
                message_lines.append("  Claims:")
                for c in p['claims']:
                    message_lines.append(f"    - {c}")
            else:
                message_lines.append("  Claims: None")
            message_lines.append("")

        message = "\n".join(message_lines)

        # Send email to admin
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [admin_email],
                fail_silently=False,
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send email: {e}")

        return redirect('index')

    return render(request, 'inquiry/index.html')
