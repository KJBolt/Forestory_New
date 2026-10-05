{
    'name': 'GeoiWorks HR Payroll Accounting',
    'category': 'Generic Modules/Human Resources',
    'author': 'GeoiWorks',
    'version': '17.0.1.0.2',
    'sequence': 2,
    'license': 'LGPL-3',
    'summary': 'Generic Payroll system Integrated with Accounting',
    'description': """Generic Payroll system Integrated with Accounting.""",
    'depends': [
        'geoiworks_payroll',
        'account'
    ],
    'data': [
        'views/hr_payroll_account_views.xml'
    ],
    'images': ['static/description/banner.png'],
    'application': True,
}
