from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class SalonAppointment(models.Model):
    _name = "salon.appointment"
    _description = "Salon Appointment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_dt asc"

    name = fields.Char(string="Reference", default="New", copy=False, readonly=True, tracking=True)

    partner_id = fields.Many2one("res.partner", string="Customer", required=True, tracking=True)
    phone = fields.Char(string="Phone", related="partner_id.phone", store=True, readonly=False)

    service_product_id = fields.Many2one(
        "product.product",
        string="Service",
        required=True,
        domain=[("type", "=", "service")],
        tracking=True,
    )

    barber_user_id = fields.Many2one(
        "res.users",
        string="Barber/Stylist",
        required=True,
        tracking=True,
    )

    start_dt = fields.Datetime(string="Start", required=True, tracking=True)
    duration_min = fields.Integer(string="Service Duration (min)", default=30, tracking=True)

    buffer_before_min = fields.Integer(string="Buffer Before (min)", default=0, tracking=True)
    buffer_after_min = fields.Integer(string="Buffer After (min)", default=5, tracking=True)

    end_dt = fields.Datetime(string="End", compute="_compute_end_dt", store=True, tracking=True)

    price = fields.Monetary(string="Price", compute="_compute_price", store=True)
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
        readonly=True
    )

    source = fields.Selection(
        [
            ("walk_in", "Walk-in"),
            ("instagram", "Instagram"),
            ("call", "Call"),
            ("website", "Website"),
        ],
        string="Source",
        default="walk_in",
        tracking=True,
    )

    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("confirmed", "Confirmed"),
            ("in_service", "In Service"),
            ("done", "Completed"),
            ("cancelled", "Cancelled"),
            ("no_show", "No Show"),
        ],
        string="Status",
        default="requested",
        tracking=True,
    )

    notes = fields.Text(string="Notes")

    # ---------- Computes ----------
    @api.depends("start_dt", "duration_min", "buffer_before_min", "buffer_after_min")
    def _compute_end_dt(self):
        for rec in self:
            if not rec.start_dt:
                rec.end_dt = False
                continue
            total = (rec.duration_min or 0) + (rec.buffer_before_min or 0) + (rec.buffer_after_min or 0)
            rec.end_dt = rec.start_dt + timedelta(minutes=total)

    @api.depends("service_product_id")
    def _compute_price(self):
        for rec in self:
            rec.price = rec.service_product_id.lst_price if rec.service_product_id else 0.0

    # ---------- Create ----------
    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = seq.next_by_code("salon.appointment") or _("New")
        return super().create(vals_list)

    # ---------- Constraints ----------
    @api.constrains("service_product_id")
    def _check_service_product_is_service(self):
        """
        Validate that selected product is a service type.
        Compatible check across Odoo versions.
        """
        for rec in self:
            p = rec.service_product_id
            if not p:
                continue

            # Check product type - works across different Odoo versions
            tmpl = getattr(p, "product_tmpl_id", None)
            ptype = getattr(p, "type", None) or (getattr(tmpl, "type", None) if tmpl else None)

            if ptype and ptype != "service":
                raise ValidationError(_("Selected product must be a Service type."))

    @api.constrains("barber_user_id", "start_dt", "end_dt", "state")
    def _check_no_overlap(self):
        """
        Prevent overlapping appointments for the same barber when state is confirmed/in_service.
        Requested appointments are allowed to overlap (so receptionist can hold requests).
        """
        active_states = ("confirmed", "in_service")
        for rec in self:
            if not rec.barber_user_id or not rec.start_dt or not rec.end_dt:
                continue
            if rec.state not in active_states:
                continue

            # overlap condition: start < other_end AND end > other_start
            domain = [
                ("id", "!=", rec.id),
                ("barber_user_id", "=", rec.barber_user_id.id),
                ("state", "in", list(active_states)),
                ("start_dt", "<", rec.end_dt),
                ("end_dt", ">", rec.start_dt),
            ]
            if self.search_count(domain):
                raise ValidationError(
                    _("This barber already has a confirmed appointment overlapping this time.")
                )

    # ---------- Buttons / Workflow ----------
    def action_confirm(self):
        for rec in self:
            rec.state = "confirmed"

    def action_in_service(self):
        for rec in self:
            rec.state = "in_service"

    def action_done(self):
        for rec in self:
            rec.state = "done"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"

    def action_no_show(self):
        for rec in self:
            rec.state = "no_show"
