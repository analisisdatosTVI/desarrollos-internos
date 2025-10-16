import io
from flask import send_file, request

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from . import controllers
from .calendar_view import choose_utils
from models import apartament_maintenance_path, apartament_weekday_calendar_starts


@controllers.route('/generate_pdf')
def generate_pdf():
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    apartment = request.args.get('apartament', 204, type=int)

    maintenance_path = apartament_maintenance_path.get(apartment, 1)
    weekday_start = apartament_weekday_calendar_starts.get(apartment, 1)
    idx_maker, _, _ = choose_utils(apartment)

    # selected fractions
    sel = request.args.getlist('fractions', type=str)
    sel = [int(f) if f.isdigit() else f for f in sel]

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    y = 750

    pdf.drawString(100, y, f"Usage dates for fractions: {', '.join(map(str, sel))}")
    y -= 20

    for yr in range(start_year, end_year + 1):
        frac_idx = idx_maker(yr, weekday_start, maintenance_path)
        pdf.drawString(100, y, f"Year {yr}")
        y -= 20

        for date, (frac, *_ ) in frac_idx.items():
            if frac in sel:
                pdf.drawString(100, y, date.strftime("%Y-%m-%d"))
                y -= 20

                if y < 50:
                    pdf.showPage()
                    y = 750

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"fractions_{start_year}_{end_year}.pdf",
        mimetype='application/pdf'
    )