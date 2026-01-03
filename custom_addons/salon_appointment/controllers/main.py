from odoo import http
from odoo.http import request
from datetime import datetime

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

    @http.route(['/appointment/submit'], type='http', auth="public", website=True, methods=['POST'])
    def appointment_submit(self, **post):
        """
        Handle form submission.
        """
        service_id = int(post.get('service_product_id'))
        employee_id = int(post.get('employee_id'))
        start_dt_str = post.get('start_dt') # Expecting format '2023-10-27T10:00' from datetime-local input
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
            start_dt = datetime.strptime(start_dt_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            # Fallback or error handling
            return request.render("salon_appointment.appointment_form", {
                'error': "Invalid date format.",
                'services': request.env['product.product'].sudo().search([('type', '=', 'service')]),
                'barbers': request.env['hr.employee'].sudo().search([('job_id.is_salon_role', '=', True)]),
            })

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
