from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_partner = fields.Boolean(string='Is a Partner', default=False)
    
    partnership_status = fields.Selection([
        ('draft', 'Draft'),
        ('signed', 'Signed'),
        ('terminated', 'Terminated')
    ], string='Partnership Status')

    partnership_type_ids = fields.Many2many('partner.partnership.type', string='Partnership Types')

    partnership_pdf = fields.Binary(string='Partnership PDF')

    signature_transaction_count = fields.Integer(
        string='Signature Transaction Count (All Time)',
        compute='_compute_signature_transaction_count',
        store=True
    )
    
    signature_transaction_count_this_year = fields.Integer(
        string='Signature Transaction Count This Year',
        compute='_compute_signature_transaction_count_this_year',
        store=True
    )
    
    client_count = fields.Integer(
        string='Number of Clients',
        compute='_compute_client_count',
        store=True
    )
    
    
    current_transaction_price = fields.Float(
        string='Current Transaction Price',
        compute='_compute_current_transaction_price',
        store=True,
        digits=(10, 4)
    )
    
    paid_transactions_this_year = fields.Float(
        string='Paid Transactions This Year',
        compute='_compute_paid_transactions_this_year',
        store=True,
        digits=(10, 2)
    )
    
    overpaid = fields.Float(
        string='Overpaid',
        compute='_compute_overpaid',
        store=True,
        digits=(10, 2)
    )

    @api.depends('child_ids.sale_order_ids.state', 'child_ids.sale_order_ids.order_line.product_id.is_signature_pack')
    def _compute_signature_transaction_count(self):
        for partner in self:
            count = 0
            # Get all child contacts
            children = partner.child_ids
            if children:
                # Find confirmed sales orders for children
                domain = [
                    ('partner_id', 'in', children.ids),
                    ('state', '=', 'sale') # confirmed orders
                ]
                orders = self.env['sale.order'].search(domain)
                
                for order in orders:
                    for line in order.order_line:
                        if line.product_id.is_signature_pack:
                            sig_count = line.product_id.signature_count or 0
                            count += (line.product_uom_qty * sig_count)
            
            partner.signature_transaction_count = count

    @api.depends('child_ids.sale_order_ids.state', 'child_ids.sale_order_ids.order_line.product_id.is_signature_pack', 'child_ids.sale_order_ids.date_order')
    def _compute_signature_transaction_count_this_year(self):
        from datetime import datetime
        for partner in self:
            count = 0
            # Get all child contacts
            children = partner.child_ids
            if children:
                # Get current year
                current_year = datetime.now().year
                # Find confirmed sales orders for children from this year
                domain = [
                    ('partner_id', 'in', children.ids),
                    ('state', '=', 'sale'),
                    ('date_order', '>=', f'{current_year}-01-01'),
                    ('date_order', '<=', f'{current_year}-12-31')
                ]
                orders = self.env['sale.order'].search(domain)
                
                for order in orders:
                    for line in order.order_line:
                        if line.product_id.is_signature_pack:
                            sig_count = line.product_id.signature_count or 0
                            count += (line.product_uom_qty * sig_count)
            
            partner.signature_transaction_count_this_year = count

    @api.depends('child_ids')
    def _compute_client_count(self):
        for partner in self:
            partner.client_count = len(partner.child_ids)

    @api.depends('signature_transaction_count_this_year')
    def _compute_current_transaction_price(self):
        # Prefetch tiers ordered by min_quantity descending
        tiers = self.env['partner.signature.tier'].search([], order='min_quantity desc')
        
        for partner in self:
            price = 0.0
            for tier in tiers:
                if partner.signature_transaction_count_this_year >= tier.min_quantity:
                    price = tier.transaction_price
                    break
            partner.current_transaction_price = price

    @api.depends('child_ids.sale_order_ids.state', 'child_ids.sale_order_ids.order_line.price_subtotal', 'child_ids.sale_order_ids.date_order')
    def _compute_paid_transactions_this_year(self):
        from datetime import datetime
        for partner in self:
            total_paid = 0.0
            # Get all child contacts
            children = partner.child_ids
            if children:
                # Get current year
                current_year = datetime.now().year
                # Find confirmed sales orders for children from this year
                domain = [
                    ('partner_id', 'in', children.ids),
                    ('state', '=', 'sale'),
                    ('date_order', '>=', f'{current_year}-01-01'),
                    ('date_order', '<=', f'{current_year}-12-31')
                ]
                orders = self.env['sale.order'].search(domain)
                
                for order in orders:
                    for line in order.order_line:
                        # Include signature pack lines, exclude discount lines
                        if line.product_id.is_signature_pack:
                            # Check if the line has the discount reference
                            if not (hasattr(line, 'name') and 'transaction-plan-upgrade-discount' in (line.name or '')):
                                total_paid += line.price_subtotal
            
            partner.paid_transactions_this_year = total_paid

    @api.depends('paid_transactions_this_year', 'current_transaction_price', 'signature_transaction_count_this_year')
    def _compute_overpaid(self):
        for partner in self:
            # Calculate what should have been paid at current tier price
            should_pay = partner.current_transaction_price * partner.signature_transaction_count_this_year
            # Calculate overpaid amount
            partner.overpaid = partner.paid_transactions_this_year - should_pay

    def action_view_child_sales(self):
        self.ensure_one()
        children = self.child_ids
        return {
            'name': 'Child Sales Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('partner_id', 'in', children.ids)],
            'context': {'default_partner_id': self.id},
        }
