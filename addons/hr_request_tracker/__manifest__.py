{
    'name': 'HR Request Tracker',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Track and manage HR requests from employees',
    'description': """
        HR Request Tracker
        ==================
        This module allows employees to submit HR requests and HR managers to track and process them.
    """,
    'author': 'Yassine',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/users.xml',
        'views/hr_request_views.xml',
        'views/hr_request_kanban.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
