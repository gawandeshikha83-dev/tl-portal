from django.urls import path

from .views import (
    dashboard,
    employee_login,
    employee_logout,
    tl_records,
    add_tl,
    edit_tl,
    delete_tl,
    tl_detail,
    thank_you,
    reports,
    excel_download,
    excel_upload,
    pdf_download,
    serve_pdf,
    pdf_viewer,
)

urlpatterns = [

    path(
        '',
        dashboard,
        name='dashboard'
    ),

    path(
        'login/',
        employee_login,
        name='employee_login'
    ),

    path(
        'logout/',
        employee_logout,
        name='employee_logout'
    ),

    path(
        'tl-records/',
        tl_records,
        name='tl_records'
    ),

    path(
        'tl-records/add/',
        add_tl,
        name='add_tl'
    ),

    path(
        'tl-records/edit/<int:pk>/',
        edit_tl,
        name='edit_tl'
    ),

    path(
        'tl-records/delete/<int:pk>/',
        delete_tl,
        name='delete_tl'
    ),

    path(
        'tl-records/detail/<int:pk>/',
        tl_detail,
        name='tl_detail'
    ),

    path(
        'thank-you/',
        thank_you,
        name='thank_you'
    ),

    path(
        'reports/',
        reports,
        name='reports'
    ),

    path(
        'excel-upload/',
        excel_upload,
        name='excel_upload'
    ),

    path(
        'excel-download/',
        excel_download,
        name='excel_download'
    ),

    path(
        'pdf-download/',
        pdf_download,
        name='pdf_download'
    ),

    path(
        'tl-records/<int:pk>/pdf/<str:file_type>/',
        serve_pdf,
        name='serve_pdf'
    ),
    
    path(
        'pdf-viewer/',
        pdf_viewer,
        name='pdf_viewer'
    ),
]