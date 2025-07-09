{
    "name": "Sales Customisation",
    "version": "1.0",
    "category": "Sales",
    "summary": "Customisation: Print flag on product and sales order line",
    "depends": ['base',"sale_management", "product"],
    "data": [
        'security/ir.model.access.csv',
        "data/product_data.xml",
        "views/product_template_views.xml",
        "views/sale_order_line_views.xml",
        "views/product_search_view.xml",
        "views/offer_type.xml"
    ],
    "installable": True,
    "application": False
}
