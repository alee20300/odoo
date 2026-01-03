from odoo import fields, models

class HrJob(models.Model):
    _inherit = "hr.job"

    is_salon_role = fields.Boolean(
        string="Is a Salon Role",
        help="Check this box if employees with this job title can be assigned to salon appointments."
    )
