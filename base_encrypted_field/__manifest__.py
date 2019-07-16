# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    'name': "Encrypted Fields",
    'summary': """Implementation of encrypted fields.""",
    'category': 'Technical Settings',
    "version": "11.0.1.0.0",
    "license": "LGPL-3",
    "author": "Modoolar",
    "website": "https://www.modoolar.com/",
    "images": ["static/description/banner.png"],
    "depends": ["base"],
    "external_dependencies": {
        "python": [
            'cryptography'
        ],
    },
    'data': [
        'views/views.xml',
    ],
}
