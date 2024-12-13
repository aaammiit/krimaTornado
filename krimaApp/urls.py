
from django.contrib import admin
from django.urls import path
from .import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    # Admin Urls
    path('',v.Index_Page),
    # Admin Dashboard Url
    path('dashboard',v.AdminDashboard),
    path('logout_user',v.Logout_user),
    # Admin Uploaded file Data View url
    path('view_file/<int:id>',v.Admin_file_view),
    # Delete File
    path('delete_file/<int:id>',v.Delete),
    # Push File To Qc
    path('push/<int:id>',v.Push_to_Qc),
    # Send Files History Url
    path('qc_file_record',v.Qc_history),
    # Editor received Url
    path('ed_file_record',v.Ed_record),
    # All user List
    path('all_user',v.All_user),
    # Download File
    path('Download/<int:id>',v.Download),
    # About-us url
    path('about_us',v.About),
    # Feature Page
    path('feature',v.Feature),
    # # delete user
    # path('d_user/<int:id>',v.Delete_user),


    # Qc User Profile Create Url
    path('make_qc',v.Make_Qc),
    # Qc User Login Url
    path('qc_login',v.QC_login), 
    # Otp Verification Url
    path('verify_otp',v.verify_otp),
    # QC Dashboard Url
    path('qc_home',v.QC_home),
    # QC Profile Show Url
    path('qc_view_file/<int:id>',v.QC_file_view),
    # Delete File
    path('del_qc/<int:id>',v.Delete_qc),
    # QC Apply Filter
    path('filter_srh/<int:id>',v.Qc_filter),
    # Qc Edit file Data
    path('qc_edit_data/<int:id>/<int:pid>',v.Qc_edit_date),
    # Qc AFter Filetr edit data
    path('qc_edit_filter_data/<int:id>/<int:pid>',v.Qc_filter_edit),
    # Qc Bulk-Edit Url
    path('data_srh/<int:id>',v.Bulk_Data_save),
    # Add Rows\Copy Data Full row Url
    path('Add_rows/<int:id>/<int:pid>',v.Add_rows),
    # Filter After Add rows Url
    path('filter_Add_rows/<int:id>/<int:pid>',v.filter_Add_rows),
    # Qc Delete Rows
    path('qc_delete_data/<int:id>/<int:pid>/',v.Delete_row),
    # File Send To Final Editor
    path('qc_push/<int:id>',v.Send_file),
    

     # Editor User Profile Create Url
    path('make_ed',v.Make_ed),
    # Editor Login url
    path('ed_login',v.ED_login),
    # Otp Verification Url
    path('verify_otp1',v.verify_otp1),
     # Editor Dashboard Url
    path('ed_home',v.ED_home),
    path('ed_view_file/<int:id>',v.Ed_file_view),
    # Editor Apply Filter
    path('ed_filter_srh/<int:id>',v.Ed_filter),
    # Editor Bulk-Edit Url
    path('ed_data_srh/<int:id>',v.Ed_Bulk_Data_save),
    # Editor Edit file Data
    path('ed_edit_data/<int:id>/<int:pid>',v.Ed_edit_date),
    # Editor AFter Filetr edit data
    path('ed_edit_filter_data/<int:id>/<int:pid>',v.Ed_filter_edit),
    # Final File Send To Admin For Download
    path('ed_push/<int:id>',v.Ed_Send_file),
    # Error/Doubts Url
    # path('message/<int:id>',v.Message),
]
