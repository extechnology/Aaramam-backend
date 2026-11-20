import csv
import io
from datetime import datetime
from django.http import HttpResponse
from django.utils import timezone
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# Column definitions: (Header Label, accessor_key_or_callable, width_hint, text_align)
SERVICE_INQUIRY_COLUMNS = [
    ('ID', 'id', 8, 'center'),
    ('Guest Name', 'name', 24, 'left'),
    ('Phone Number', 'phone_number', 18, 'center'),
    ('Email Address', 'email', 26, 'left'),
    ('Package Name', lambda o: o.service.title if o.service else 'General Inquiry', 32, 'left'),
    ('Package Category', lambda o: o.service.category.name if (o.service and o.service.category) else '-', 22, 'left'),
    ('Status', lambda o: o.get_status_display(), 14, 'center'),
    ('Message / Notes', 'message', 40, 'left'),
    ('Submission Date', lambda o: timezone.localtime(o.created_at).strftime('%Y-%m-%d %H:%M') if o.created_at else '-', 20, 'center'),
]

ADMISSION_INQUIRY_COLUMNS = [
    ('ID', 'id', 8, 'center'),
    ('Applicant Name', 'name', 24, 'left'),
    ('Phone / WhatsApp', 'phone_number', 18, 'center'),
    ('Email Address', 'email', 26, 'left'),
    ('Program / Treatment', lambda o: o.get_program_display() if hasattr(o, 'get_program_display') else o.program, 30, 'left'),
    ('Bystander Accommodation', lambda o: o.get_bystander_accommodation_display() if hasattr(o, 'get_bystander_accommodation_display') else o.bystander_accommodation, 26, 'left'),
    ('Requirements / Due Date', 'requirements_or_due_date', 36, 'left'),
    ('Doctor / Sanctuary Notes', 'notes', 36, 'left'),
    ('Status', lambda o: o.get_status_display(), 14, 'center'),
    ('Submission Date', lambda o: timezone.localtime(o.created_at).strftime('%Y-%m-%d %H:%M') if o.created_at else '-', 20, 'center'),
]

GUEST_FEEDBACK_COLUMNS = [
    ('ID', 'id', 8, 'center'),
    ('Guest Name', 'name', 24, 'left'),
    ('Phone Number', 'phone_number', 18, 'center'),
    ('Email Address', 'email', 26, 'left'),
    ('Treatment Experienced', 'treatment_taken', 28, 'left'),
    ('Rating', lambda o: f"{o.rating} / 5 ★", 14, 'center'),
    ('Feedback / Review', 'feedback', 44, 'left'),
    ('Approval Status', lambda o: 'Approved' if o.is_approved else 'Pending Approval', 18, 'center'),
    ('Submission Date', lambda o: timezone.localtime(o.created_at).strftime('%Y-%m-%d %H:%M') if o.created_at else '-', 20, 'center'),
]


def _extract_val(obj, accessor):
    """Safely extracts value from an object attribute or callable."""
    if callable(accessor):
        try:
            val = accessor(obj)
        except Exception:
            val = '-'
    else:
        val = getattr(obj, accessor, '')
    if val is None:
        return ''
    return str(val).strip()


def export_to_csv(queryset, filename: str, columns: list) -> HttpResponse:
    """
    Exports a queryset to a CSV file with utf-8-sig encoding for perfect Excel compatibility.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    timestamp_str = timezone.localtime().strftime('%Y%m%d_%H%M')
    clean_filename = f"{filename}_{timestamp_str}.csv"
    response['Content-Disposition'] = f'attachment; filename="{clean_filename}"'

    writer = csv.writer(response)
    # Header row
    writer.writerow([col[0] for col in columns])

    # Data rows
    for obj in queryset:
        row = [_extract_val(obj, col[1]) for col in columns]
        writer.writerow(row)

    return response


def export_to_excel(queryset, filename: str, sheet_title: str, columns: list) -> HttpResponse:
    """
    Exports a queryset to a beautifully styled Excel (.xlsx) workbook using openpyxl.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title[:31]  # Excel sheet title limit is 31 chars

    # Palette: Aaramam Sanctuary Obsidian & Forest Emerald
    TITLE_FILL = PatternFill(start_color='0E2A1E', end_color='0E2A1E', fill_type='solid')
    HEADER_FILL = PatternFill(start_color='143E2C', end_color='143E2C', fill_type='solid')
    ZEBRA_FILL = PatternFill(start_color='F8FAF8', end_color='F8FAF8', fill_type='solid')
    WHITE_FILL = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')

    TITLE_FONT = Font(name='Calibri', size=15, bold=True, color='D4AF37')  # Gold
    SUBTITLE_FONT = Font(name='Calibri', size=10, italic=True, color='94A3B8')
    HEADER_FONT = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    BODY_FONT = Font(name='Calibri', size=10, color='1E293B')

    THIN_BORDER_SIDE = Side(border_style='thin', color='E2E8F0')
    BORDER_ALL = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=THIN_BORDER_SIDE, bottom=THIN_BORDER_SIDE)
    HEADER_BORDER = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=THIN_BORDER_SIDE, bottom=Side(border_style='medium', color='D4AF37'))

    STATUS_FILLS = {
        'new': PatternFill(start_color='FEF3C7', end_color='FEF3C7', fill_type='solid'),      # Yellow
        'pending': PatternFill(start_color='FEF3C7', end_color='FEF3C7', fill_type='solid'),
        'contacted': PatternFill(start_color='DBEAFE', end_color='DBEAFE', fill_type='solid'),# Blue
        'converted': PatternFill(start_color='DCFCE7', end_color='DCFCE7', fill_type='solid'),# Green
        'confirmed': PatternFill(start_color='DCFCE7', end_color='DCFCE7', fill_type='solid'),
        'approved': PatternFill(start_color='DCFCE7', end_color='DCFCE7', fill_type='solid'),
        'closed': PatternFill(start_color='FEE2E2', end_color='FEE2E2', fill_type='solid'),   # Red
    }

    # Row 1: Brand Title
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(columns))
    title_cell = ws.cell(row=1, column=1)
    title_cell.value = f"AARAMAM AYURVEDA SANCTUARY — {sheet_title.upper()}"
    title_cell.font = TITLE_FONT
    title_cell.fill = TITLE_FILL
    title_cell.alignment = Alignment(horizontal='left', vertical='center', indent=1)
    ws.row_dimensions[1].height = 36

    # Row 2: Metadata / Timestamp
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(columns))
    now_str = timezone.localtime().strftime('%d %B %Y, %I:%M %p')
    meta_cell = ws.cell(row=2, column=1)
    meta_cell.value = f"Generated on {now_str} • Total Records: {queryset.count()} • Confidential Sanctuary Portal"
    meta_cell.font = SUBTITLE_FONT
    meta_cell.fill = PatternFill(start_color='081B13', end_color='081B13', fill_type='solid')
    meta_cell.alignment = Alignment(horizontal='left', vertical='center', indent=1)
    ws.row_dimensions[2].height = 20

    # Row 3: Blank spacing row
    ws.row_dimensions[3].height = 8

    # Row 4: Column Headers
    header_row_idx = 4
    ws.row_dimensions[header_row_idx].height = 28
    for col_idx, col in enumerate(columns, start=1):
        cell = ws.cell(row=header_row_idx, column=col_idx)
        cell.value = col[0]
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = HEADER_BORDER
        cell.alignment = Alignment(horizontal=col[3], vertical='center', wrap_text=True)

    # Freeze panes below headers
    ws.freeze_panes = f"A{header_row_idx + 1}"

    # Data Rows
    current_row = header_row_idx + 1
    for r_idx, obj in enumerate(queryset):
        row_fill = ZEBRA_FILL if r_idx % 2 == 1 else WHITE_FILL
        ws.row_dimensions[current_row].height = 22

        for col_idx, col in enumerate(columns, start=1):
            cell = ws.cell(row=current_row, column=col_idx)
            val = _extract_val(obj, col[1])
            cell.value = val
            cell.font = BODY_FONT
            cell.border = BORDER_ALL
            cell.alignment = Alignment(horizontal=col[3], vertical='center')

            # Highlight status pills
            if col[0].lower() in ['status', 'approval status']:
                lower_val = val.lower()
                for key, fill in STATUS_FILLS.items():
                    if key in lower_val:
                        cell.fill = fill
                        cell.font = Font(name='Calibri', size=10, bold=True, color='0F172A')
                        break
                else:
                    cell.fill = row_fill
            else:
                cell.fill = row_fill

        current_row += 1

    # Auto-adjust column widths based on hint or content
    for col_idx, col in enumerate(columns, start=1):
        col_letter = get_column_letter(col_idx)
        hint_width = col[2] if len(col) > 2 else 15
        ws.column_dimensions[col_letter].width = max(hint_width, 12)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    timestamp_str = timezone.localtime().strftime('%Y%m%d_%H%M')
    clean_filename = f"{filename}_{timestamp_str}.xlsx"
    response = HttpResponse(
        buf.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{clean_filename}"'
    return response
