from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    service_duration = fields.Float(
        string="Service Duration (Hours)", 
        help="Duration of the service in hours.",
        default=0.5
    )
