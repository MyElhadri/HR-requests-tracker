from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HrRequest(models.Model):
    _name = 'hr.request'
    _description = 'HR Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc, id desc'

    name = fields.Char(
        string='Reference', 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: _('New')
    )
    title = fields.Char(string='Title', required=True, tracking=True)
    employee_id = fields.Many2one(
        'hr.employee', 
        string='Employee', 
        required=True, 
        default=lambda self: self.env.user.employee_id, 
        tracking=True
    )
    request_type = fields.Selection([
        ('certificate', 'Certificate'),
        ('document_request', 'Document Request'),
        ('hr_question', 'HR Question'),
        ('payroll_question', 'Payroll Question'),
        ('other', 'Other')
    ], string='Request Type', required=True, tracking=True)
    description = fields.Text(string='Description', required=True)
    hr_response = fields.Text(string='HR Response', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status', default='draft', tracking=True, copy=False)
    
    # Safely evaluating the domain context by matching group strings to prevent uninitialized registry registry crashes
    responsible_id = fields.Many2one(
        'res.users', 
        string='Responsible HR', 
        tracking=True, 
        domain="[('groups_id.category_id.name', '=', 'HR Request Tracker'), ('groups_id.name', '=', 'HR Manager')]"
    )
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1', tracking=True)
    
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today, readonly=True)
    done_date = fields.Date(string='Done Date', readonly=True)
    processing_duration = fields.Integer(string='Processing Duration (Days)', compute='_compute_processing_duration', store=True)
    active = fields.Boolean(default=True)

    @api.depends('request_date', 'done_date')
    def _compute_processing_duration(self):
        for record in self:
            if record.request_date and record.done_date:
                delta = record.done_date - record.request_date
                record.processing_duration = delta.days
            else:
                record.processing_duration = 0

    @api.depends('name', 'title')
    def _compute_display_name(self):
        for record in self:
            name = record.name or _('New')
            title = record.title or ''
            record.display_name = f"[{name}] {title}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.request') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        is_manager = self.env.user.has_group('hr_request_tracker.group_hr_request_manager')
        
        # SÉCURITÉ GLOBALE : Personne ne peut modifier le statut manuellement (même les HR Managers)
        if 'state' in vals and not self.env.context.get('allow_state_change'):
            raise UserError(_('You cannot change the status manually. Please use the workflow buttons.'))

        if not is_manager:
            # SÉCURITÉ EMPLOYÉ 1: Bloquer strictement les champs RH
            strict_hr_fields = ['hr_response', 'responsible_id', 'done_date']
            if any(field in vals for field in strict_hr_fields):
                raise UserError(_('You are not allowed to modify HR specific fields (HR response, responsible, done date).'))
                
            # SÉCURITÉ EMPLOYÉ 2: Vérifier la légitimité de la transition de statut
            if 'state' in vals:
                for record in self:
                    if record.state != 'draft' or vals['state'] != 'submitted':
                        raise UserError(_('You can only submit requests from Draft to Submitted.'))
                    if record.employee_id.user_id != self.env.user:
                        raise UserError(_('You can only submit your own requests.'))

            # SÉCURITÉ EMPLOYÉ 3: Empêcher la modification de la demande une fois soumise
            for record in self:
                if record.state != 'draft' and any(field in vals for field in ['title', 'request_type', 'description', 'priority']):
                    raise UserError(_('You cannot modify a request once it is submitted.'))
        return super().write(vals)

    def action_submit(self):
        is_manager = self.env.user.has_group('hr_request_tracker.group_hr_request_manager')
        for record in self:
            if not is_manager and record.employee_id.user_id != self.env.user:
                 raise UserError(_('You can only submit your own requests.'))
            if record.state != 'draft':
                raise UserError(_('Only draft requests can be submitted.'))
        
        self.with_context(allow_state_change=True).write({'state': 'submitted'})

    def action_start_processing(self):
        if not self.env.user.has_group('hr_request_tracker.group_hr_request_manager'):
            raise UserError(_('Only HR Managers can start processing a request.'))
            
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted requests can be processed.'))
        self.with_context(allow_state_change=True).write({
            'state': 'in_progress',
            'responsible_id': self.env.user.id
        })

    def action_mark_done(self):
        if not self.env.user.has_group('hr_request_tracker.group_hr_request_manager'):
            raise UserError(_('Only HR Managers can mark a request as done.'))
            
        for record in self:
            if record.state != 'in_progress':
                raise UserError(_('Only in-progress requests can be marked as done.'))
        self.with_context(allow_state_change=True).write({
            'state': 'done',
            'done_date': fields.Date.context_today(self)
        })

    def action_reset_draft(self):
        if not self.env.user.has_group('hr_request_tracker.group_hr_request_manager'):
            raise UserError(_('Only HR Managers can reset a request to draft.'))
            
        self.with_context(allow_state_change=True).write({
            'state': 'draft',
            'done_date': False,
            'responsible_id': False
        })

    @api.ondelete(at_uninstall=False)
    def _unlink_except_not_draft(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_('You can only delete requests in Draft state.'))