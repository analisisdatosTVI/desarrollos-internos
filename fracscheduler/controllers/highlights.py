import io
from datetime import datetime, timedelta
from flask import send_file, request
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from . import controllers
from .calendar_view import choose_utils
from models import apartament_maintenance_path, apartament_weekday_calendar_starts, apartament_type
from utils import parameters


def get_week_date_ranges(year, weekday_start, maintenance_path, fraction, apartment):
    """
    Get all week date ranges for a specific fraction over 8 years.
    Returns list of tuples: (start_date, end_date, year)
    """
    apt_type = apartament_type.get(apartment, "regular")
    idx_maker, _, _ = choose_utils(apartment)
    
    all_weeks = []
    
    # Determine starting year based on apartment type
    if apt_type == "snow":
        # For snow apartments, we need to check if we're before or after Sept 22
        today = datetime.now().date()
        season_start = parameters.first_day_snow(year)
        if today < season_start:
            start_year = year - 1
        else:
            start_year = year
    else:
        start_year = year
    
    # Collect 8 years of data
    for yr in range(start_year, start_year + 8):
        frac_idx = idx_maker(yr, weekday_start, maintenance_path)
        
        # Group consecutive dates by week
        current_week_dates = []
        for date_obj in sorted(frac_idx.keys()):
            frac_list = frac_idx[date_obj]
            if frac_list[0] == fraction:
                if not current_week_dates:
                    current_week_dates.append(date_obj)
                elif (date_obj - current_week_dates[-1]).days == 1:
                    current_week_dates.append(date_obj)
                else:
                    # Week complete, add to all_weeks
                    if len(current_week_dates) >= 6:  # Valid week
                        all_weeks.append((
                            current_week_dates[0],
                            current_week_dates[-1],
                            current_week_dates[0].year
                        ))
                    current_week_dates = [date_obj]
        
        # Add last week if exists
        if len(current_week_dates) >= 6:
            all_weeks.append((
                current_week_dates[0],
                current_week_dates[-1],
                current_week_dates[0].year
            ))
    
    return all_weeks


def format_date_spanish(date_obj):
    """Convert date to Spanish format: '5 de enero de 2026'"""
    months_es = [
        '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]
    return f"{date_obj.day} de {months_es[date_obj.month]} de {date_obj.year}"


def format_date_short_spanish(date_obj):
    """Convert date to short Spanish format: '5 ene 2026'"""
    months_es_short = [
        '', 'ene', 'feb', 'mar', 'abr', 'may', 'jun',
        'jul', 'ago', 'sep', 'oct', 'nov', 'dic'
    ]
    return f"{date_obj.day} {months_es_short[date_obj.month]} {date_obj.year}"


def draw_header(pdf, width, height, apartment, display_fraction):
    """Draw header on page"""
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(width / 2, height - 0.6 * inch, "SEMANAS ASIGNADAS")
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(width / 2, height - 0.85 * inch, f"Apartamento {apartment} - Fracción {display_fraction}")


def draw_table_header(pdf, x, y, col_widths):
    """Draw table header row"""
    pdf.setFillColor(colors.HexColor('#147f95'))
    pdf.rect(x, y - 0.25 * inch, sum(col_widths), 0.25 * inch, fill=True, stroke=False)
    
    pdf.setFillColor(colors.whitesmoke)
    pdf.setFont("Helvetica-Bold", 9)
    
    headers = ["Año", "Semana", "Inicio", "Fin"]
    current_x = x
    for i, header in enumerate(headers):
        pdf.drawCentredString(current_x + col_widths[i] / 2, y - 0.17 * inch, header)
        current_x += col_widths[i]
    
    pdf.setFillColor(colors.black)


def draw_table_row(pdf, x, y, row_data, col_widths, is_even):
    """Draw a single table row"""
    # Background
    if is_even:
        pdf.setFillColor(colors.HexColor('#f8f9fa'))
        pdf.rect(x, y - 0.22 * inch, sum(col_widths), 0.22 * inch, fill=True, stroke=False)
        pdf.setFillColor(colors.black)
    
    # Border
    pdf.setStrokeColor(colors.grey)
    pdf.setLineWidth(0.5)
    pdf.rect(x, y - 0.22 * inch, sum(col_widths), 0.22 * inch, fill=False, stroke=True)
    
    # Text
    pdf.setFont("Helvetica", 8)
    current_x = x
    for i, data in enumerate(row_data):
        pdf.drawCentredString(current_x + col_widths[i] / 2, y - 0.15 * inch, str(data))
        current_x += col_widths[i]


@controllers.route('/preview_pdf')
def preview_pdf():
    """Generate HTML page with embedded PDF and print button"""
    apartment = request.args.get('apartament', 205, type=int)
    fraction = request.args.get('fraction', type=int)
    
    if fraction is None:
        return "Error: No fraction specified", 400
    
    display_fraction = 8 if fraction == 0 else fraction
    
    html = f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Certificado - Apartamento {apartment} Fracción {display_fraction}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: #f5f5f5;
                overflow: hidden;
            }}
            .pdf-container {{
                width: 100vw;
                height: 100vh;
                position: relative;
            }}
            iframe {{
                width: 100%;
                height: 100%;
                border: none;
            }}
            .print-button {{
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: linear-gradient(135deg, #e85d04 0%, #c74f03 100%);
                color: white;
                border: none;
                padding: 18px 35px;
                font-size: 18px;
                font-weight: 600;
                border-radius: 50px;
                cursor: pointer;
                box-shadow: 0 8px 24px rgba(232, 93, 4, 0.4);
                display: flex;
                align-items: center;
                gap: 12px;
                transition: all 0.3s ease;
                z-index: 1000;
                animation: pulse 2s infinite;
            }}
            .print-button:hover {{
                transform: translateY(-3px);
                box-shadow: 0 12px 32px rgba(232, 93, 4, 0.5);
            }}
            .print-button:active {{
                transform: translateY(-1px);
            }}
            .print-icon {{
                font-size: 24px;
            }}
            @keyframes pulse {{
                0%, 100% {{
                    box-shadow: 0 8px 24px rgba(232, 93, 4, 0.4);
                }}
                50% {{
                    box-shadow: 0 8px 32px rgba(232, 93, 4, 0.6);
                }}
            }}
            @media print {{
                .print-button {{
                    display: none !important;
                }}
            }}
            /* Mobile optimizations */
            @media (max-width: 768px) {{
                .print-button {{
                    bottom: 20px;
                    right: 20px;
                    padding: 16px 28px;
                    font-size: 16px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="pdf-container">
            <iframe src="/generate_pdf?apartament={apartment}&fraction={fraction}" type="application/pdf"></iframe>
        </div>
        <button class="print-button" onclick="printPDF()">
            <span class="print-icon">🖨️</span>
            <span>Imprimir Documento</span>
        </button>
        
        <script>
            function printPDF() {{
                // For iframe, we need to access the iframe's window
                const iframe = document.querySelector('iframe');
                
                try {{
                    // Try to print the iframe content
                    iframe.contentWindow.focus();
                    iframe.contentWindow.print();
                }} catch (e) {{
                    // Fallback: print the whole page (which includes the PDF)
                    window.print();
                }}
            }}
            
            // Optional: Add keyboard shortcut Ctrl+P / Cmd+P
            document.addEventListener('keydown', function(e) {{
                if ((e.ctrlKey || e.metaKey) && e.key === 'p') {{
                    e.preventDefault();
                    printPDF();
                }}
            }});
        </script>
    </body>
    </html>
    '''
    
    return html


@controllers.route('/generate_pdf')
def generate_pdf():
    apartment = request.args.get('apartament', 205, type=int)
    fraction = request.args.get('fraction', type=int)
    
    if fraction is None:
        return "Error: No fraction specified", 400
    
    # Display fraction as 8 instead of 0
    display_fraction = 8 if fraction == 0 else fraction
    
    maintenance_path = apartament_maintenance_path.get(apartment, 1)
    weekday_start = apartament_weekday_calendar_starts.get(apartment, 1)
    apt_type = apartament_type.get(apartment, "regular")
    
    # Get current year
    current_year = datetime.now().year
    
    # Get all weeks for this fraction
    weeks = get_week_date_ranges(current_year, weekday_start, maintenance_path, fraction, apartment)
    
    # Create PDF
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # ============= PAGE 1: Title and Legal Information =============
    
    # Header with logo space
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(width / 2, height - 1.2 * inch, "SEASCAPE")
    
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(width / 2, height - 1.5 * inch, "Condominio de Uso Fraccionado")
    
    # Title
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(width / 2, height - 2.2 * inch, "CERTIFICADO DE ASIGNACIÓN")
    pdf.drawCentredString(width / 2, height - 2.5 * inch, "DE SEMANAS FRACCIONADAS")
    
    # Apartment and Fraction Info
    pdf.setFont("Helvetica-Bold", 14)
    y_position = height - 3.2 * inch
    pdf.drawCentredString(width / 2, y_position, f"Apartamento: {apartment}")
    y_position -= 0.4 * inch
    pdf.drawCentredString(width / 2, y_position, f"Fracción: {display_fraction}")
    
    # Date of issue
    pdf.setFont("Helvetica", 10)
    y_position -= 0.6 * inch
    fecha_emision = datetime.now().strftime("%d de %B de %Y")
    months_es = {
        'January': 'enero', 'February': 'febrero', 'March': 'marzo',
        'April': 'abril', 'May': 'mayo', 'June': 'junio',
        'July': 'julio', 'August': 'agosto', 'September': 'septiembre',
        'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    for eng, esp in months_es.items():
        fecha_emision = fecha_emision.replace(eng, esp)
    pdf.drawCentredString(width / 2, y_position, f"Fecha de emisión: {fecha_emision}")
    
    # Legal Text
    pdf.setFont("Helvetica-Bold", 12)
    y_position -= 0.8 * inch
    pdf.drawCentredString(width / 2, y_position, "DECLARACIONES")
    
    pdf.setFont("Helvetica", 9)
    y_position -= 0.3 * inch
    
    legal_text = [
        "El presente documento certifica la asignación de semanas correspondientes a la Fracción",
        f"{display_fraction} del Apartamento {apartment} en el condominio SEASCAPE, de conformidad con el",
        "Régimen de Propiedad en Condominio y el Reglamento Interno del mismo.",
        "",
        "Las semanas asignadas se encuentran distribuidas de acuerdo al sistema rotativo establecido",
        "en el ciclo de 8 años, garantizando el uso equitativo de todas las temporadas del año.",
        "",
        "Este certificado tiene validez legal y constituye comprobante oficial de los periodos de uso",
        "asignados al titular de la fracción mencionada.",
    ]
    
    for line in legal_text:
        pdf.drawCentredString(width / 2, y_position, line)
        y_position -= 0.2 * inch
    
    # Signature section
    y_position -= 0.5 * inch
    pdf.line(1.5 * inch, y_position, 3.5 * inch, y_position)
    pdf.line(4.5 * inch, y_position, 6.5 * inch, y_position)
    
    y_position -= 0.2 * inch
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(2.5 * inch, y_position, "Administración SEASCAPE")
    pdf.drawCentredString(5.5 * inch, y_position, "Titular de la Fracción")
    
    # Footer
    pdf.setFont("Helvetica-Oblique", 7)
    pdf.drawCentredString(width / 2, 0.5 * inch, "Este documento es legalmente vinculante y debe ser conservado por el titular de la fracción.")
    
    # ============= PAGE 2 onwards: Week Assignments (Manual Drawing) =============
    
    # Column widths
    col_widths = [0.75 * inch, 1 * inch, 2 * inch, 2 * inch]
    table_x = 1 * inch
    
    # Rows per page calculation
    rows_per_page = 28
    
    current_page = 2
    row_index = 0
    
    while row_index < len(weeks):
        pdf.showPage()
        
        # Draw header
        draw_header(pdf, width, height, apartment, display_fraction)
        
        # Starting Y position for table
        y = height - 1.2 * inch
        
        # Draw table header
        draw_table_header(pdf, table_x, y, col_widths)
        y -= 0.25 * inch
        
        # Draw rows
        rows_drawn = 0
        while rows_drawn < rows_per_page and row_index < len(weeks):
            start_date, end_date, year = weeks[row_index]
            week_num = start_date.isocalendar()[1]
            
            row_data = [
                str(year),
                f"Sem {week_num}",
                format_date_short_spanish(start_date),
                format_date_short_spanish(end_date)
            ]
            
            draw_table_row(pdf, table_x, y, row_data, col_widths, row_index % 2 == 0)
            
            y -= 0.22 * inch
            rows_drawn += 1
            row_index += 1
        
        # Footer
        pdf.setFont("Helvetica-Oblique", 7)
        pdf.drawCentredString(width / 2, 0.5 * inch, 
            f"SEASCAPE - Apartamento {apartment} - Fracción {display_fraction} - Página {current_page}")
        current_page += 1
    
    # Save PDF
    pdf.save()
    buffer.seek(0)
    
    filename = f"SEASCAPE_Apt{apartment}_Fraccion{display_fraction}_Semanas.pdf"
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=filename
    )