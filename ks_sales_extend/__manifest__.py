{
    "name": "Sales Customisation",
    "version": "1.0",
    "category": "Sales",
    "summary": "Customisation added like:"
               "1. EFB"
               "2. Measurement Calculation"
               "3. Add GEAB option on Sales."
               "4. Print flag on product and sales order line",
    "depends": ['base','sale_management', 'sale_project', 'product','account'],
    "data": [
        'security/ir.model.access.csv',
        'security/efb_rule.xml',
        "data/product_data.xml",
        "views/product_template_views.xml",
        "views/sale_order_line_views.xml",
        "views/product_search_view.xml",
        "views/offer_type.xml",
        "views/measurement_calulation_view.xml",
        "views/measurement_calculation_subtotal_view.xml",
        "views/project_project_view.xml",
        "views/account_move_view.xml"
    ],
    "installable": True,
    "application": True
}
