# views.py
from datetime import datetime
import os
import re
import logging
from io import BytesIO
import tempfile
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string, get_template
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from playwright.sync_api import sync_playwright
import pathlib

from .models import Inquiry


# ────────────────────────────────────────────────────────────────────
# ───────────── Helper utilities ────────────────────────────────────
# ────────────────────────────────────────────────────────────────────

def _sanitize_filename(text: str) -> str:
    """Return a filesystem-safe version of `text`."""
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', text)


def _generate_pdf_with_browser(html_path, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Convert backslashes to forward slashes for Windows
        path_uri = pathlib.Path(html_path).absolute().as_uri()
        page.goto(path_uri, wait_until='networkidle')

        page.pdf(
            path=output_path,
            format='A4',
            margin={
                "top": "20mm",
                "bottom": "20mm",
                "left": "20mm",
                "right": "20mm"
            },
            scale=1.0,  # ensure 100% scaling for consistent font/field sizes
            print_background=True  # important if using background color/shading
        )
        browser.close()


# ────────────────────────────────────────────────────────────────────
# ───────────── Main form view ──────────────────────────────────────
# ────────────────────────────────────────────────────────────────────

@csrf_exempt
def index(request):
    if request.method == 'POST':
        try:
            # ── 1.  Extract form data ───────────────────────────────────
            client_name   = request.POST.get('clientName')
            claims_type   = request.POST.get('claimsType')
            provider_name = request.POST.get('providerName')
            tax_id        = request.POST.get('taxId')
            npi           = request.POST.get('npi')

            # Patients
            patients_info, patient_idx = [], 1
            while True:
                p_name = request.POST.get(f'patient{patient_idx}Name')
                p_dob  = request.POST.get(f'patient{patient_idx}DOB')
                if not p_name or not p_dob:
                    break

                try:
                    dob_obj = datetime.strptime(p_dob, '%m-%d-%Y')
                    p_dob = dob_obj.strftime('%m/%d/%Y')    
                except ValueError:
                    pass  # keep original if not mm-dd-yyyy

                claims = []
                for i in range(1, 4):
                    dos    = request.POST.get(f'p{patient_idx}dos{i}', '').strip()
                    amount = request.POST.get(f'p{patient_idx}amount{i}', '').strip()
                    if dos or amount:
                        claims.append({
                            'date_of_service': dos,
                            'amount': amount or 0
                        })

                patients_info.append({'name': p_name, 'dob': p_dob, 'claims': claims})
                patient_idx += 1

            # ── 2.  Persist to DB ───────────────────────────────────────
            inquiry = Inquiry.objects.create(
                client_name   = client_name,
                claims_type   = claims_type,
                provider_name = provider_name,
                tax_id        = tax_id,
                npi           = npi,
                patients      = patients_info
            )

            # ── 3.  Build HTML for PDF ──────────────────────────────────
            context = {
                'client_name' : client_name,
                'claims_type' : claims_type,
                'provider_name': provider_name,
                'tax_id'      : tax_id,
                'npi'         : npi,
                'patients'    : patients_info,
            }
            html_content = render_to_string('inquiry/pdf_template.html', context)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmp_file:
                tmp_file.write(html_content)
                tmp_file_path = tmp_file.name

            # ── 4.  Render PDF with Playwright ──────────────────────────
            ts        = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = _sanitize_filename(provider_name or 'provider')
            pdf_dir   = os.path.join(settings.BASE_DIR, 'submitted_documents')
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_path  = os.path.join(pdf_dir, f"{safe_name}_{ts}.pdf")

            try:
                _generate_pdf_with_browser(tmp_file_path, pdf_path)

                # STEP 1: Ensure the PDF is fully written before reading
                import time
                for _ in range(10):  # Wait up to 1 second (10 x 0.1s)
                    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1024:  # Adjust threshold if needed
                        break
                    time.sleep(0.1)

                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()
            except Exception as e:
                logging.getLogger(__name__).error("PDF generation error: %s", e)
                return HttpResponse('Error generating PDF', status=500)
            finally:
                os.remove(tmp_file_path)  # clean temp HTML

            if not pdf_content:
                return HttpResponse('Error generating PDF', status=500)

            # ── 5.  Email PDF to Admin ──────────────────────────────────
            admin_emails = [
                'avinashkalmegh93@gmail.com',
                'tusharfuse1802@gmail.com',
                'akshay.kumar@onesmarter.com',
            ]
            subject     = 'New Missing Claims Inquiry Submitted'

            email_body = render_to_string('inquiry/email_template.html', {
                **context,
                # flatten all claim rows if your template needs them
                'claims': [c for p in patients_info for c in p.get('claims', [])]
            })

            email = EmailMessage(
                subject,
                email_body,
                settings.EMAIL_HOST_USER,
                admin_emails)
            email.content_subtype = 'html'
            email.attach(os.path.basename(pdf_path), pdf_content, 'application/pdf')

            try:
                email.send(fail_silently=False)
            except Exception as exc:
                logging.getLogger(__name__).error("Email send failure: %s", exc)
                return HttpResponse('Error sending email', status=500)

            messages.success(request, "Form submitted successfully!")
            return redirect(reverse('index') + f'?inquiry_id={inquiry.id}')
        except Exception as e:
            logging.getLogger(__name__).error("Form submission error: %s", e)
            return HttpResponse('Internal server error', status=500)

    # GET request ----------------------------------------------------
    inquiry_id = request.GET.get('inquiry_id')
    return render(request, 'inquiry/index.html', {'inquiry_id': inquiry_id} if inquiry_id else {})

    # GET request ----------------------------------------------------
    inquiry_id = request.GET.get('inquiry_id')
    return render(request, 'inquiry/index.html', {'inquiry_id': inquiry_id} if inquiry_id else {})


# ────────────────────────────────────────────────────────────────────
# ───────────── Download-PDF endpoint ───────────────────────────────
# ────────────────────────────────────────────────────────────────────

def download_pdf(request, inquiry_id):
    """Generate a fresh PDF on demand and stream it to the browser."""
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)

    ctx = {
        'client_name' : inquiry.client_name,
        'claims_type' : inquiry.claims_type,
        'provider_name': inquiry.provider_name,
        'tax_id'      : inquiry.tax_id,
        'npi'         : inquiry.npi,
        'patients'    : inquiry.patients or [],
        'administrator': inquiry.administrator,
        'telephone'   : inquiry.telephone,
        'telefax'     : inquiry.telefax,
        'email'       : inquiry.email,
    }

    html_string = get_template('inquiry/pdf_template.html').render(ctx)
    pdf_bytes   = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

    filename = f"{_sanitize_filename(inquiry.provider_name)}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
