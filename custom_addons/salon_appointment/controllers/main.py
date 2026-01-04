from odoo import http
from odoo.http import request
from datetime import datetime, timedelta

class WebsiteSalonAppointment(http.Controller):

    @http.route(['/appointment'], type='http', auth="public", website=True)
    def appointment_form(self, **kwargs):
        """
        Render the appointment booking form.
        """
        # Fetch available services and barbers
        services = request.env['product.product'].sudo().search([('type', '=', 'service')])
        # Barbers are employees with 'is_salon_role' job
        barbers = request.env['hr.employee'].sudo().search([('job_id.is_salon_role', '=', True)])
        
        values = {
            'services': services,
            'barbers': barbers,
        }
        return request.render("salon_appointment.appointment_form", values)

    @http.route(['/appointment/json/slots'], type='json', auth="public", website=True)
    def appointment_slots(self, employee_id, service_product_id, date_str):
        """
        Return available time slots for the given barber and service on a specific date.
        """
        try:
            employee = request.env['hr.employee'].sudo().browse(int(employee_id))
            product = request.env['product.product'].sudo().browse(int(service_product_id))
            
            # Parse date (YYYY-MM-DD)
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Define working hours (Simplified: 09:00 to 17:00)
            # Todo: Use employee.resource_calendar_id for real implementation
            start_hour = 9
            end_hour = 17
            
            duration_min = int(product.service_duration * 60) if product else 30
            
            # Fetch existing appointments for this barber on this day
            Appointment = request.env['salon.appointment'].sudo()
            
            # Filter for the whole day (UTC handling required in real world, simplistic here)
            day_start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
            day_end = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
            
            existing_appts = Appointment.search([
                ('employee_id', '=', employee.id),
                ('state', 'in', ['confirmed', 'in_service']),
                ('start_dt', '>=', day_start),
                ('start_dt', '<=', day_end),
            ])
            
            slots = []
            
            # Generate slots every 30 mins
            current_time = datetime(target_date.year, target_date.month, target_date.day, start_hour, 0)
            end_time = datetime(target_date.year, target_date.month, target_date.day, end_hour, 0)
            
            while current_time + timedelta(minutes=duration_min) <= end_time:
                slot_end = current_time + timedelta(minutes=duration_min)
                
                # Check overlap
                is_available = True
                for appt in existing_appts:
                    # Overlap logic: (StartA < EndB) and (EndA > StartB)
                    if (current_time < appt.end_dt) and (slot_end > appt.start_dt):
                        is_available = False
                        break
                
                if is_available:
                    slots.append({
                        'time': current_time.strftime("%H:%M"),
                        'datetime': current_time.strftime("%Y-%m-%dT%H:%M"),
                        'display': current_time.strftime("%I:%M %p"),
                    })
                
                # Step 30 mins
                current_time += timedelta(minutes=30)
                
            return {'slots': slots}
            
        except Exception as e:
            return {'error': str(e)}

    @http.route(['/appointment/submit'], type='http', auth="public", website=True, methods=['POST'])
    def appointment_submit(self, **post):
        """
        Handle form submission.
        """
        service_id = int(post.get('service_product_id'))
        employee_id = int(post.get('employee_id'))
        start_dt_str = post.get('start_dt') # Expecting format '2023-10-27T10:00' from datetime-local or hidden input
        name = post.get('name')
        phone = post.get('phone')
        notes = post.get('notes')

        # Find or create partner based on phone/name
        Partner = request.env['res.partner'].sudo()
        partner = Partner.search([('phone', '=', phone)], limit=1)
        if not partner:
            partner = Partner.create({
                'name': name,
                'phone': phone,
            })
        
        # Convert datetime-local string to datetime object
        # Input format is usually "YYYY-MM-DDTHH:MM"
        try:
            # Try ISO format first (from JS) or datetime-local
            if 'T' in start_dt_str:
                start_dt = datetime.strptime(start_dt_str, "%Y-%m-%dT%H:%M")
            else:
                 # Fallback if just time passed (unlikely)
                 start_dt = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M:%S")

        except ValueError:
            # Fail gracefully
            return request.redirect('/appointment?error=date_format')

        # Create Appointment
        Appointment = request.env['salon.appointment'].sudo()
        appointment = Appointment.create({
            'partner_id': partner.id,
            'service_product_id': service_id,
            'employee_id': employee_id,
            'start_dt': start_dt,
            'notes': notes,
            'source': 'website',
            'state': 'requested',
        })

        return request.render("salon_appointment.appointment_thanks", {'appointment': appointment})
