from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from .models import *
from datetime import datetime
from krimaProject import settings
import json
import os
import smtplib
import random
import math
import copy
import pandas as pd
from django.urls import reverse
import openpyxl

# GMAIL-SMTP Cred.
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'amistreetecom0101@gmail.com'
SMTP_PASSWORD = 'xmxj ztoo dfvw bxtm'
sender_email = 'amistreetecom0101@gmail.com' 


# Index Page Views/logic Function
def Index_Page(request):
    if request.method=='POST':
        u=request.POST.get('un')
        p=request.POST.get('p')
        user=authenticate(User,username=u,password=p)  
        try: 
            if user.is_staff:
                request.session['uid']=user.id
                login(request,user)
                err='no' 
                messages.success(request,'Admin, you have logged in successfully.')
                return redirect('/dashboard')                
        except:
            # messages.error(request,'Something Went Wrong Please Try Againg')
            err='yes'                                
    return render(request,'admin_temps/index.html')

# Admin Home Page Function
def AdminDashboard(request):
    
    user=request.user
    file_data=My_Upload_file.objects.all() 
    qc=Qc_user.objects.all()
    data={'data':file_data,'qc':qc}
    try:
        list_date=[]
        date_obj=[]
        if request.method=='POST':
            u=My_Upload_file()
            fsh=request.FILES.get('file')
            print(fsh)
            u.file=fsh
            u.save()
        with open(f'{settings.BASE_DIR}//{fsh}','r') as f:
            f1=json.load(f)
        u.count=len(f1)
        u.o_len=len(f1)
        for i in f1:
            if i['Date'] != 'None' or i['Date'] != 'null':
               list_date.append((i['Date']))
        for i in list_date:
            date_str =str(i)
            datetime_object = datetime.strptime(date_str,'%Y-%m-%d')
            date_object = datetime_object.date()
            date_obj.append(date_object)
        sorted_date=sorted(date_obj)
        u.from_date=sorted_date[0]
        u.to_date=sorted_date[-1]
        u.save()
        messages.success(request,'File Uploaded Successfully')
        return redirect('/dashboard')
    except Exception as e:
        print(e)
        ...
        # messages.error(request,'Something Went Wrong Here Please Try Again Later')  
    return render(request,'admin_temps/admin_home.html',data)


# All User's Logout Function   
def Logout_user(request):
    logout(request)
    messages.success(request,'Your Profile Logout Successfully')
    return redirect('/')

# Admin File Delete Logic Function
def Delete(request,id):
    u=My_Upload_file.objects.get(id=id)
    file=u.file
    os.remove(f'{settings.BASE_DIR}//{file}')
    u.delete()
    return redirect('/dashboard')
# from django.shortcuts import get_object_or_404, redirect
# def Delete_user(request, id):
#     qc = get_object_or_404(Qc_user, id=id)
#     user = get_object_or_404(User, id=qc.user_id)
#     user.delete()
#     qc.delete()  # Delete qc after the user to avoid potential cascading issues
#     return redirect('/all_user')

# Admin File Data view Function
def Admin_file_view(request,id):
    list_date=[]
    date_obj=[]
    from_date=''
    to_date=''
    user=request.user
    
    try:    
        file_obj=My_Upload_file.objects.get(id=id)
        file_obj1=My_Upload_file.objects.filter(id=id)
        for i in file_obj1:
            file=i.file
        with open(f'{settings.BASE_DIR}//{file}','r') as f:
            f1=json.load(f)
        for i in f1:
            if i['Date'] != 'None' or i['Date'] != 'null':
               list_date.append((i['Date']))
        for i in list_date:
            date_str =i
            datetime_object = datetime.strptime(date_str,'%Y-%m-%d')
            date_object = datetime_object.date()
            date_obj.append(date_object)
        sorted_date=sorted(date_obj)
        from_date=sorted_date[0]
        to_date=sorted_date[-1] 
        data={'data':f1,'f':from_date,'t':to_date}      
    except:
        ...
    return render(request,'admin_temps/view_file.html',data)

# All user's List Show Functio
def All_user(request):
    
    user_types = {
        'QC': Qc_user.objects.all(),
        'Editor': ED_User.objects.all()
    }
    return render(request,'admin_temps/All_user.html',{'user_types':user_types})

# Admin File's no of records Alocate To QC function 
def Push_to_Qc(request,id):
    user=request.user
    file_obj1=My_Upload_file.objects.filter(id=id)
    for i in file_obj1:
        file=i.file
        date=i.date
    with open(f'{settings.BASE_DIR}//{file}','r') as f:
        f1=json.load(f)
    name=file.name
    length=len(f1)
    date=date    
    if request.method == 'POST':
        my_file = My_Upload_file.objects.get(id=id)
        file_name = request.POST.get('file_name')
        user_id = request.POST.get('user')
        end_index = int(request.POST.get('end'))
        print(end_index)
        # Load the original file
        file_path = f'{settings.BASE_DIR}/{my_file.file}'
        with open(file_path, 'r') as file:
            data = json.load(file)
        # Extract the desired chunk from the original file
        chunk = data[0:end_index]
        # print(chunk)
        # Create a new QC data instance
        qc = my_Qc_data()
        qc.qc_file = f'{file_name}.json'
        qc.my_file = my_file
        qc.end = end_index
        qc.user = Qc_user.objects.get(id=user_id)
        qc.save()
        # Save the chunk to a new file
        chunk_file_path = f'{settings.BASE_DIR}/{qc.qc_file}'
        if not os.path.exists(chunk_file_path):
            with open(chunk_file_path, 'w') as file:
                json.dump(chunk, file)
        else:
            print(f"File {chunk_file_path} already exists.")
        # Update the original file by removing the chunk
        data = data[end_index:]
        with open(file_path, 'w') as file:
            json.dump(data, file)
        # Extract dates from the updated original file
        dates = [datetime.strptime(item['Date'], '%Y-%m-%d').date() for item in data if item['Date'] not in ['None', 'null']]
        if dates:
            my_file.from_date = min(dates)
            my_file.to_date = max(dates)
        else:
            my_file.from_date = None
            my_file.to_date = None
        my_file.count = len(data)
        my_file.status=True
        my_file.save()
        # Extract dates from the chunk file
        with open(chunk_file_path, 'r') as file:
            chunk_data = json.load(file)
        dates = [datetime.strptime(item['Date'], '%Y-%m-%d').date() for item in chunk_data if item['Date'] not in ['None', 'null']]
        if dates:
            qc.from_date = min(dates)
            qc.to_date = max(dates)
        else:
            qc.from_date = None
            qc.to_date = None
        qc.save()
        with open(f'{settings.BASE_DIR}/{qc.qc_file}','r+') as f:
            f.seek(0)  # move file pointer to the beginning of the file
            f1 = json.load(f)
            for item in f1:
                item['Ok'] = 0
                item['method']=''
            f.seek(0)  # move file pointer to the beginning of the file again
            json.dump(f1, f)
            f.truncate()  # remove any remaining characters after the new JSON data
        messages.success(request,'File Send Successfully To Qc User')
        return redirect('/dashboard')
    else:
        form = qc_Form()
    return render(request,'admin_temps/push_form.html',{'form': form,'name':name,'length':length,'date':date})

# Admin Alocate file's Record History function
def Qc_history(request):
    data=my_Qc_data.objects.all()
    stats = []
    combined_list=[]
    for qc_data in data:
        file_path = f'{settings.BASE_DIR}//{qc_data.qc_file}'
        with open(file_path, 'r') as f:
            qc_file_data = json.load(f)

        counts = {
            'correct': 0,
            'error': 0,
            'rejected': 0,
            'unclassified': 0,
            'bulk':0
           
        }


        for item in qc_file_data:
            
            if item['Ok'] == '1':
                counts['correct'] += 1
            elif item['Ok'] == '0':
                counts['error'] += 1
            elif item['Ok'] == '2':
                counts['rejected'] += 1
            elif item['method'] == 'Bulk Edit':
                counts['bulk'] += 1
                
            else:
                counts['unclassified'] += 1


        stats.append(counts)
        combined_list = list(zip(data, stats))
        

    return render(request, 'admin_temps/qc_record.html', {
        'combined_list':combined_list
    })
   
# QC Profile Makeing By Admin Function
def Make_Qc(request):
    user=request.user
   
    err=''
   
    if request.method=='POST':
        f_n=request.POST.get('f_n')
        l_n=request.POST.get('l_n')  
        email=request.POST.get('email')
        p=request.POST.get('p')
        try:
            user=User.objects.create_user(first_name=f_n,last_name=l_n,email=email,username=email,password=p)
            Qc_user.objects.create(user=user)
            err='no'
            messages.success(request,'QC Profile Created Successfully')    
            return redirect('/dashboard')
        except:
            err='yes'     
    return render(request,'qc_temps/make_qc.html')

# QC User Login Function 
def QC_login(request):
    if request.method == 'POST':
        u = request.POST.get('email')
        p = request.POST.get('p')
        user = authenticate(User, username=u, password=p)
        if user is not None:
            request.session['uid'] = user.id
            receiver_email = u
            otp_length = 6
            otp = math.floor(random.random() * 10**(otp_length-1) + 10**(otp_length-1))
            # Send OTP via email
            subject = "OTP Verification"
            body = f"Your OTP is: {otp}"
            try:
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(sender_email, receiver_email, f"Subject: {subject}\n\n{body}")
                server.quit()
                print("OTP sent successfully")    
                # Store OTP in session
                request.session['otp'] = otp   
                # Redirect to OTP verification page
                return redirect('/verify_otp')
            except:
                err = 'yes'
                return render(request, 'qc_temps/qc_login.html', locals())
        else:
            err = 'yes'
            return render(request, 'qc_temps/qc_login.html', locals())
    return render(request, 'qc_temps/qc_login.html', locals())

# Qc Login Otp Verification Function
def verify_otp(request):
    us=request.session.get('uid')
    user=User.objects.get(id=us)
    # print(user)      
    if request.method == 'POST':
        otp_user = request.POST.get('otp')
        otp_session = request.session.get('otp')
        if otp_user == str(otp_session):
            msg = 'Successfully Verified'
            login(request, user)
            err = 'no'
            messages.success(request,'Login Successfully')
            return redirect('/qc_home')
        else:
            msg = 'Invalid OTP'
            err = 'yes'
            return render(request, 'qc_temps/verify_otp.html', locals())
    return render(request, 'qc_temps/verify_otp.html', locals()) 

# Qc Dashboard Function
def QC_home(request):
    ed=ED_User.objects.all()
    pid=request.session.get('uid')
    user=Qc_user.objects.get(user=pid)
    data=my_Qc_data.objects.filter(user=user)
    stats = []
    for qc_data in data:
        file_path = f'{settings.BASE_DIR}//{qc_data.qc_file}'
        with open(file_path, 'r') as f:
            qc_file_data = json.load(f)

        counts = {
            'correct': 0,
            'error': 0,
            'rejected': 0,
            'unclassified': 0,
           
        }


        for item in qc_file_data:
            
            if item['Ok'] == '1':
                counts['correct'] += 1
            elif item['Ok'] == '0':
                counts['error'] += 1
            elif item['Ok'] == '2':
                counts['rejected'] += 1
            else:
                counts['unclassified'] += 1


        stats.append(counts)
        combined_list = list(zip(data, stats))
    
    return render(request, 'qc_temps/qc_home.html', {
        'data': data,
        'stats':stats,
        'ed':ed
    })

# Qc View File Function
def QC_file_view(request,id):
    list_date=[]
    date_obj=[]
    from_date=''
    to_date=''
    file_id=0
    pid=request.session.get('uid')
    user=Qc_user.objects.get(user=pid)
    
    try:   
        check,uncheck,err,reject=0,0,0,0 
        file_obj=my_Qc_data.objects.get(id=id)
        file_obj1=my_Qc_data.objects.filter(id=id)
        for i in file_obj1:
            file=i.qc_file
            file_id=i.id
            status=i.status
        with open(f'{settings.BASE_DIR}//{file}','r') as f:
            f1=json.load(f)
        for i in range(len(f1)):
            if f1[i]['Ok'] =='1':
                check+=1
            elif f1[i]['Ok'] =='0':
                err+=1
            elif f1[i]['Ok'] =='2':
                reject+=1
            else:
                uncheck+=1
        for i in f1:
            if i['Date'] != 'None' or i['Date'] != 'null':
               list_date.append((i['Date']))
        for i in list_date:
            date_str =i
            datetime_object = datetime.strptime(date_str,'%Y-%m-%d')
            date_object = datetime_object.date()
            date_obj.append(date_object)
        sorted_date=sorted(date_obj)
        from_date=sorted_date[0]
        to_date=sorted_date[-1] 
        data={'data':f1,'f':from_date,'t':to_date,'id':file_id,'c':check,'e':err,'uc':uncheck,'rj':reject,'status':status}     
    except:
        return render(request,'qc_temps/qc_view.html',)
    return render(request,'qc_temps/qc_view.html',data)

def Delete_qc(request,id):
    u=my_Qc_data.objects.get(id=id)
    file=u.qc_file
    os.remove(f'{settings.BASE_DIR}//{file}')
    u.delete()
    return redirect('/qc_file_record') 


# DElete Rows Of file
def Delete_row(request, id, pid):
    file_obj = my_Qc_data.objects.get(id=id)
    file = file_obj.qc_file
    with open(f'{settings.BASE_DIR}//{file}', 'r+') as f:
        original_data = json.load(f)
        del original_data[pid]
        f.seek(0)
        json.dump(original_data, f, indent=4)
        f.truncate()
    return redirect(f'/qc_view_file/{id}')

# Qc Apply Filter Function
def Qc_filter(request,id):
    pid=request.session.get('uid')
    user=Qc_user.objects.get(user=pid)
    file_obj = my_Qc_data.objects.get(id=id)
    file_path = f'{settings.BASE_DIR}/{file_obj.qc_file}'
    with open(file_path, 'r') as f:
        original_data = json.load(f)
    if request.method == 'POST':
        keywords = [
            request.POST.get('keyword'),
            request.POST.get('keyword1'), 
        ]

        filters = [
            request.POST.get('fil1'),
            request.POST.get('fil2'),
        ]

        key2= request.POST.get('keyword2')
        fil3= request.POST.get('fil3')
        sort_type = request.POST.get('st')
        sort_column = request.POST.get('sc')
        data = original_data[:]  # Create a copy of the original data
        # Filter data based on keywords
        for keyword, filter_column in zip(keywords, filters):
            if keyword:
                data = [item for item in data if str(keyword).strip() in str(item.get(filter_column, ''))]
        # Filter data based on fil3 and key2
        if fil3 and key2 and fil3 != 'Filter 3 Choose...':
            data = [item for item in data if item[fil3] == key2]
        # Sort data based on sort type and column if provided
        if sort_type and sort_column:
            if sort_type == 'z-a':
                data = sorted(data, key=lambda x: x[sort_column], reverse=True)
            elif sort_type == 'a-z':
                data = sorted(data, key=lambda x: x[sort_column])
        request.session['data_re'] = data
    data_record = {'data': data, 'length': len(data), 'id': file_obj.id}
    return render(request, 'qc_temps/filter.html', data_record)

# Qc File Edit Function
def Qc_edit_date(request,id,pid):
    pid=pid
    id=id
    pide=request.session.get('uid')
    user=Qc_user.objects.get(user=pide)
    if request.method=='POST':
        a7=request.POST.get('a7')
        a8=request.POST.get('a8')
        a9=request.POST.get('a9')
        a10=request.POST.get('a10')
        a11=request.POST.get('a11')
        a12=request.POST.get('a12')
        a13=request.POST.get('a13')
        a14=request.POST.get('a14')
        a15=request.POST.get('a15')
        a16=request.POST.get('a16')
        a17=request.POST.get('a17')
        a18=request.POST.get('a18')
        a19=request.POST.get('a19')
        a20=request.POST.get('a20')
        a21=request.POST.get('a21')
        a22=request.POST.get('a22')

        a23=request.POST.get('a23')
        a24=request.POST.get('a24')
        a25=request.POST.get('a25')
        a26=request.POST.get('a26')
        file_obj = my_Qc_data.objects.get(id=id)
        file = file_obj.qc_file
        id=file_obj.id
        with open(f'{settings.BASE_DIR}//{file}', 'r') as f:
            data = json.load(f)
        data[pid]['KRIMA_status']=a7
        data[pid]['KRIMA_true_false']=a8
        data[pid]['KRIMA_type']=a9
        data[pid]['KRIMA_notes']=a10
        data[pid]['KRIMA_edited_gpt_person_or_business']=a11
        data[pid]['KRIMA_edited_gpt_company_check']=a12
        data[pid]['parent_company_name']=a13
        data[pid]['KRIMA_civil_penalty_validated']=a14
        data[pid]['KRIMA_civil_penalty_cleansed']=a15
        data[pid]['KRIMA_currency']=a16
        data[pid]['KRIMA_civil_penalty_usd']=a17
        data[pid]['KRIMA_disgorgement_restitution_usd']=a18
        data[pid]['KRIMA_imposed_penalty']=a19
        data[pid]['KRIMA_settled_value']=a20
        data[pid]['KRIMA_non_monetary_penalty']=a21
        data[pid]['Ok']=a22

        data[pid]['gpt_area_of_activity_or_service']=a23
        data[pid]['gpt_area_of_regulation']=a24
        data[pid]['KRIMA_area_of_activity_or_service']=a25
        data[pid]['KRIMA_area_of_regulation']=a26
        with open(f'{settings.BASE_DIR}//{file}', 'w') as f:
            json.dump(data,f)
        return redirect(f'/qc_view_file/{id}')
    else:
        file_obj = my_Qc_data.objects.get(id=id)
        file = file_obj.qc_file
        id=file_obj.id
        with open(f'{settings.BASE_DIR}//{file}', 'r') as f:
            data = json.load(f)
        sr_no=data[pid]['sr_no']
        Article=data[pid]['Article']
        gpt=data[pid]['gpt_summary']
        Date=data[pid]['Date']
        Regulatory=data[pid]['Regulatory']
        Title=data[pid]['Title']
        URL=data[pid]['URL']
        KRIMA_status=data[pid]['KRIMA_status']
        KRIMA_true_false=data[pid]['KRIMA_true_false']
        KRIMA_type=data[pid]['KRIMA_type']
        KRIMA_notes=data[pid]['KRIMA_notes']
        KRIMA_edited_gpt_person_or_business=data[pid]['KRIMA_edited_gpt_person_or_business']
        KRIMA_edited_gpt_company_check=data[pid]['KRIMA_edited_gpt_company_check']
        parent_company_name=data[pid]['parent_company_name']
        KRIMA_civil_penalty_validated=data[pid]['KRIMA_civil_penalty_validated']
        KRIMA_civil_penalty_cleansed=data[pid]['KRIMA_civil_penalty_cleansed']
        KRIMA_currency=data[pid]['KRIMA_currency']
        KRIMA_civil_penalty_usd=data[pid]['KRIMA_civil_penalty_usd']
        KRIMA_disgorgement_restitution_usd=data[pid]['KRIMA_disgorgement_restitution_usd']
        KRIMA_imposed_penalty=data[pid]['KRIMA_imposed_penalty']
        KRIMA_settled_value=data[pid]['KRIMA_settled_value']
        KRIMA_non_monetary_penalty=data[pid]['KRIMA_non_monetary_penalty']
        ok=data[pid]['Ok']
        gpt_area_of_activity_or_service=data[pid]['gpt_area_of_activity_or_service']
        gpt_area_of_regulation=data[pid]['gpt_area_of_regulation']
        KRIMA_area_of_activity_or_service=data[pid]['KRIMA_area_of_activity_or_service']
        KRIMA_area_of_regulation=data[pid]['KRIMA_area_of_regulation']
    return render(request,'qc_temps/edit.html',locals())

# # Qc After Apply Filter Then Edit file Function
def Qc_filter_edit(request, id, pid):
    pide = request.session.get('uid')
    user = Qc_user.objects.get(user=pide)
    file_obj = my_Qc_data.objects.get(id=id)
    file = file_obj.qc_file
    id = file_obj.id
    data = request.session.get('data_re')

    if request.method == 'POST':
        fields = {
            'sr_no': 'a1',
            'Date': 'a2',
            'Regulatory': 'a3',
            'Title': 'a4',
            'KRIMA_status': 'a7',
            'KRIMA_true_false': 'a8',
            'KRIMA_type': 'a9',
            'KRIMA_notes': 'a10',
            'KRIMA_edited_gpt_person_or_business': 'a11',
            'KRIMA_edited_gpt_company_check': 'a12',
            'parent_company_name': 'a13',
            'KRIMA_civil_penalty_validated': 'a14',
            'KRIMA_civil_penalty_cleansed': 'a15',
            'KRIMA_currency': 'a16',
            'KRIMA_civil_penalty_usd': 'a17',
            'KRIMA_disgorgement_restitution_usd': 'a18',
            'KRIMA_imposed_penalty': 'a19',
            'KRIMA_settled_value': 'a20',
            'KRIMA_non_monetary_penalty': 'a21',
            'Ok': 'a22',
            'gpt_area_of_activity_or_service':'a23',
            'gpt_area_of_regulation':'a24',
            'KRIMA_area_of_activity_or_service':'a25',
            'KRIMA_area_of_regulation':'a26',
        }

        # Load the JSON file
        with open(f'{settings.BASE_DIR}/{file}', 'r') as f:
            data1 = json.load(f)

        # Find the index where the sr_no matches
        for index, item in enumerate(data1):
            if item['sr_no'] == data[pid]['sr_no']:
                # Update only the fields specified in the fields dictionary
                for field, key in fields.items():
                    item[field] = request.POST.get(key)
                data1[index] = item
                data[pid]=data1[index]
                dt=data[pid]
        data[pid]=dt

        # Save the updated data to the JSON file
        with open(f'{settings.BASE_DIR}/{file}', 'w') as f:
            json.dump(data1, f)
        # print('done')
        da = {'data': data, 'id': id}
        return render(request, 'qc_temps/filter.html', da)

    else:
        uid = pid
        context = {
            'sr_no': data[pid]['sr_no'],
            'Article': data[pid]['Article'],
            'Date': data[pid]['Date'],
            'Regulatory': data[pid]['Regulatory'],
            'Title': data[pid]['Title'],
            'URL': data[pid]['URL'],
            'KRIMA_status': data[pid]['KRIMA_status'],
            'KRIMA_true_false': data[pid]['KRIMA_true_false'],
            'KRIMA_type': data[pid]['KRIMA_type'],
            'KRIMA_notes': data[pid]['KRIMA_notes'],
            'KRIMA_edited_gpt_person_or_business': data[pid]['KRIMA_edited_gpt_person_or_business'],
            'KRIMA_edited_gpt_company_check': data[pid]['KRIMA_edited_gpt_company_check'],
            'parent_company_name': data[pid]['parent_company_name'],
            'KRIMA_civil_penalty_validated': data[pid]['KRIMA_civil_penalty_validated'],
            'KRIMA_civil_penalty_cleansed': data[pid]['KRIMA_civil_penalty_cleansed'],
            'KRIMA_currency': data[pid]['KRIMA_currency'],
            'KRIMA_civil_penalty_usd': data[pid]['KRIMA_civil_penalty_usd'],
            'KRIMA_disgorgement_restitution_usd': data[pid]['KRIMA_disgorgement_restitution_usd'],
            'KRIMA_imposed_penalty': data[pid]['KRIMA_imposed_penalty'],
            'KRIMA_settled_value': data[pid]['KRIMA_settled_value'],
            'KRIMA_non_monetary_penalty': data[pid]['KRIMA_non_monetary_penalty'],
            'ok': data[pid]['Ok'],
            'pid': uid,
            'id': id,
            'gpt_area_of_activity_or_service':data[pid]['gpt_area_of_activity_or_service'],
            'gpt_area_of_regulation':data[pid]['gpt_area_of_regulation'],
            'KRIMA_area_of_activity_or_service':data[pid]['KRIMA_area_of_activity_or_service'],
            'KRIMA_area_of_regulation':data[pid]['KRIMA_area_of_regulation'],
            'gpt':data[pid]['gpt_summary']
            
            }
        return render(request, 'qc_temps/filter_edit.html', context)

# Qc Bulk Edit Function
def Bulk_Data_save(request, id):
    data = request.session.get('data_re')
    if request.method == 'POST':
        words = [
            request.POST.get('Words1'),
            request.POST.get('Words2'),
            request.POST.get('Words3'),

        ]
        columns = [
            request.POST.get('col1'),
            request.POST.get('col2'),
            request.POST.get('col3')
        ]
        # Filter out empty words and columns
        words = [word for word in words if word]
        columns = [column for column in columns if column]
        file_obj = my_Qc_data.objects.get(id=id)
        file_path = f'{settings.BASE_DIR}/{file_obj.qc_file}'
        with open(file_path, 'r') as f:
            original_data = json.load(f)
        if not columns or columns[0] == "None":
            # Replace entire row with words
            for i, item in enumerate(original_data):
                if item in data:
                    original_data[i] = [word for word in words for _ in item]
                    original_data[i].append({"method": "Bulk Edit"})
                   
        else:
            # Replace specific column with words
            header = original_data[0]
            for i, item in enumerate(original_data):
                if item in data:
                    for column, word in zip(columns, words):
                        if column not in header:
                            print(f'Error: Column "{column}" not found')
                            return redirect('/qc_home')
                        column_key = list(header.keys())[list(header.keys()).index(column)]
                        item[column_key] = word
                        item["method"] = "Bulk Edit"
        with open(file_path, 'w') as f:
            json.dump(original_data, f)
        return redirect(f'/qc_view_file/{id}')
    return redirect('/qc_home')

# Qc Add Row/Copy Record Function
def Add_rows(request, id, pid):
    pide=request.session.get('uid')
    user=Qc_user.objects.get(user=pide)
    if request.method == 'POST':
        file_obj = my_Qc_data.objects.get(id=id)
        file = file_obj.qc_file
        id = file_obj.id
        with open(f'{settings.BASE_DIR}//{file}', 'r') as f:
            data1 = json.load(f)
        No_rec = request.POST.get('no_rec')
        no_rec = int(No_rec)
        # Get the record at position pid
        record_to_copy = data1[pid]  # subtract 1 because pid is 1-indexed
        # Copy the record no_rec times and append to the data
        for i in range(no_rec):
            data1.append(copy.deepcopy(record_to_copy))
            print('done')
        # Save the updated data back to the file
        with open(f'{settings.BASE_DIR}//{file}', 'w') as f:
            json.dump(data1, f)
        return redirect(f'/qc_view_file/{id}')
    else:
        print('no')    
    data={'id':id,'pid':pid}
    return render(request,'qc_temps/add_row.html',data)

# Qc After Apply Filter then Add Rows Or copy rows Function
def filter_Add_rows(request,id,pid):
    pide=request.session.get('uid')
    user=Qc_user.objects.get(user=pide)
    file_obj = my_Qc_data.objects.get(id=id)
    file = file_obj.qc_file
    data = request.session.get('data_re')
    if request.method == 'POST':
        no_rec = int(request.POST.get('no_rec'))  
        # Get the record at position pid (assuming pid is 0-indexed)
        record_to_copy = data[pid]
        # Copy the record no_rec times and append to the data
        new_data = []
        for _ in range(no_rec):
            new_data.append(copy.deepcopy(record_to_copy))
        # Load the existing data from the file
        with open(f'{settings.BASE_DIR}/{file}', 'r') as f:
            existing_data = json.load(f)
        # Append the new data to the existing data
        existing_data.extend(new_data)
        # Save the updated data back to the file
        with open(f'{settings.BASE_DIR}/{file}', 'w') as f:
            json.dump(existing_data, f)
        return redirect(f'/qc_view_file/{id}')
    else:
        print('no')
    context = {'id': id, 'pid': pid}
    return render(request, 'qc_temps/add_row.html', context)

# Qc Send File To Editor Function
def Send_file(request,id):
    upid = request.session.get('uid')
    user = Qc_user.objects.get(user=upid)
    qc_data = my_Qc_data.objects.get(id=id)
    name=qc_data.qc_file
    with open(f'{settings.BASE_DIR}/{name}', 'r') as f:
            f1=json.load(f)
    length=len(f1)
    date=qc_data.date
    if request.method == 'POST':
        form = pushForm(request.POST)
        if form.is_valid():
            ed_ed = form.cleaned_data['Editior']
            qc_data = my_Qc_data.objects.get(id=id)
            file=qc_data.qc_file
            with open(f'{settings.BASE_DIR}/{file}', 'r') as f:
                f1=json.load(f)
           

            length=len(f1)
            qc_data.status = True
            try:
                ed_push = Editor_push(
                    Editior=ed_ed,
                    qc_data=qc_data,
                    qc_user=user,
                    rec_length=length,
                )
                ed_push.save()
                qc_data.save()
                messages.success(request,'File Sended Successfully')
                return redirect('/qc_home')
            except Exception as e:
                print(f"Error: {e}")
                return render(request, 'editior_temps/push_ed.html', {'form': form})
    else:
        form = pushForm()
    return render(request, 'editior_temps/push_ed.html', {'form': form,'name':name,'length':length,'date':date})

# Editor Profile Make By Admin Function
def Make_ed(request):
    user=request.user
    err=''
   
    if request.method=='POST':
        f_n=request.POST.get('f_n')
        l_n=request.POST.get('l_n')  
        email=request.POST.get('email')
        p=request.POST.get('p')
        try:
            user=User.objects.create_user(first_name=f_n,last_name=l_n,email=email,username=email,password=p)
            ED_User.objects.create(user=user)
            err='no'  
            messages.success(request,'Editor Profile Created Successfully')  
            return redirect('/dashboard')
        except:
            err='yes'
    return render(request,'editior_temps/make_ed.html')

# Editor Login Function
def ED_login(request):
    if request.method == 'POST':
        u = request.POST.get('email')
        p = request.POST.get('p')
        user = authenticate(User, username=u, password=p)
        if user is not None:
            request.session['uid'] = user.id
            receiver_email = u
            otp_length = 6
            otp = math.floor(random.random() * 10**(otp_length-1) + 10**(otp_length-1))
            # Send OTP via email
            subject = "OTP Verification"
            body = f"Your OTP is: {otp}"
            try:
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(sender_email, receiver_email, f"Subject: {subject}\n\n{body}")
                server.quit()
                print("OTP sent successfully")    
                # Store OTP in session
                request.session['otp'] = otp   
                # Redirect to OTP verification page
                return redirect('/verify_otp1')
            except:
                err = 'yes'
                return render(request, 'editior_temps/ed_login.html', locals())
        else:
            err = 'yes'
            return render(request, 'editior_temps/ed_login.html', locals())
    return render(request,'editior_temps/ed_login.html')
        
# Editor Login Otp Verification Function
def verify_otp1(request):
    us=request.session.get('uid')
    user=User.objects.get(id=us)
    # print(user)      
    if request.method == 'POST':
        otp_user = request.POST.get('otp')
        otp_session = request.session.get('otp')
        if otp_user == str(otp_session):
            msg = 'Successfully Verified'
            login(request, user)
            err = 'no'
            messages.success(request,'Login Successfully')
            return redirect('/ed_home')
        else:
            msg = 'Invalid OTP'
            err = 'yes'
            return render(request, 'qc_temps/verify_otp.html', locals())
    return render(request, 'qc_temps/verify_otp.html', locals()) 

# Editor dashboard Function
def ED_home(request):
    upid = request.session.get('uid')
    user = ED_User.objects.get(user=upid)
    data=Editor_push.objects.filter(Editior=user)
    return render(request,'editior_temps/ed_home.html',{'data':data})

# Editor Profile Show on Page Function
def Ed_profile(request):
    try:
        pid=request.session.get('uid')
        user=ED_User.objects.get(user=pid)
       
        # data=ED_profile.objects.get(user=user)
    except:
        return redirect('/ed_home')
    return render(request,'editior_temps/ed_profile.html')

# Editor Profile Setup Function


# Editor View File Function    
def Ed_file_view(request,id):
    list_date=[]
    date_obj=[]
    from_date=''
    to_date=''
    file_id=0
    pid=request.session.get('uid')
    user=ED_User.objects.get(user=pid)
    try: 
        check,err,uncheck,reject=0,0,0,0   
        file_obj=Editor_push.objects.get(id=id)
        file_obj1=Editor_push.objects.filter(id=id)
        for i in file_obj1:
            file=i.qc_data.qc_file
            file_id=i.id
            status=i.sta
        with open(f'{settings.BASE_DIR}//{file}','r') as f:
            f1=json.load(f)
        for i in range(len(f1)):
            if f1[i]['Ok'] =='1':
                check+=1
            elif f1[i]['Ok'] =='0':
                err+=1
            elif f1[i]['Ok'] =='2':
                reject+=1
            else:
                uncheck+=1
        for i in f1:
            if i['Date'] != 'None' or i['Date'] != 'null':
               list_date.append((i['Date']))
        for i in list_date:
            date_str =i
            datetime_object = datetime.strptime(date_str,'%Y-%m-%d')
            date_object = datetime_object.date()
            date_obj.append(date_object)
        sorted_date=sorted(date_obj)
        from_date=sorted_date[0]
        to_date=sorted_date[-1] 
        data={'data':f1,'f':from_date,'t':to_date,'id':file_id,'status':status,'c':check,'uc':uncheck,'e':err,'rj':reject}     
    except:
        return render(request,'editior_temps/ed_view.html',)
    return render(request,'editior_temps/ed_view.html',data)

# Editor Apply Filter Function
def Ed_filter(request,id):
    pid=request.session.get('uid')
    user=ED_User.objects.get(user=pid)
    file_obj = Editor_push.objects.get(id=id)
    status=file_obj.sta
    file_path = f'{settings.BASE_DIR}/{file_obj.qc_data.qc_file}'
    with open(file_path, 'r') as f:
        original_data = json.load(f)
    if request.method == 'POST':
        keywords = [
            request.POST.get('keyword'),
            request.POST.get('keyword1'), 
        ]

        filters = [
            request.POST.get('fil1'),
            request.POST.get('fil2'),
        ]

        key2= request.POST.get('keyword2')
        fil3= request.POST.get('fil3')
        sort_type = request.POST.get('st')
        sort_column = request.POST.get('sc')
        data = original_data[:]  # Create a copy of the original data
        # Filter data based on keywords
        for keyword, filter_column in zip(keywords, filters):
            if keyword:
                data = [item for item in data if str(keyword).strip() in str(item.get(filter_column, ''))]
        # Filter data based on fil3 and key2
        if fil3 and key2 and fil3 != 'Filter 3 Choose...':
            data = [item for item in data if item[fil3] == key2]
        # Sort data based on sort type and column if provided
        if sort_type and sort_column:
            if sort_type == 'z-a':
                data = sorted(data, key=lambda x: x[sort_column], reverse=True)
            elif sort_type == 'a-z':
                data = sorted(data, key=lambda x: x[sort_column])
        request.session['data_re'] = data
    data_record = {'data': data, 'length': len(data), 'id': file_obj.id,'status':status}
    return render(request, 'editior_temps/ed_filter.html', data_record)
    

# Editor Bulk Edit Function
def Ed_Bulk_Data_save(request, id):
    data = request.session.get('data_re')
    if request.method == 'POST':
        words = [
            request.POST.get('Words1'),
            request.POST.get('Words2'),
            request.POST.get('Words3')
        ]
        columns = [
            request.POST.get('col1'),
            request.POST.get('col2'),
            request.POST.get('col3')
        ]
        # Filter out empty words and columns
        words = [word for word in words if word]
        columns = [column for column in columns if column]
        file_obj = Editor_push.objects.get(id=id)
        file_path = f'{settings.BASE_DIR}/{file_obj.qc_data.qc_file}'
        with open(file_path, 'r') as f:
            original_data = json.load(f)
        if not columns or columns[0] == "None":
            # Replace entire row with words
            for i, item in enumerate(original_data):
                if item in data:
                    original_data[i] = [word for word in words for _ in item]
        else:
            # Replace specific column with words
            header = original_data[0]
            for i, item in enumerate(original_data):
                if item in data:
                    for column, word in zip(columns, words):
                        if column not in header:
                            print(f'Error: Column "{column}" not found')
                            return redirect('/ed_home')
                        column_key = list(header.keys())[list(header.keys()).index(column)]
                        item[column_key] = word
        with open(file_path, 'w') as f:
            json.dump(original_data, f)
        return redirect(f'/ed_view_file/{id}')
    return redirect('/ed_home')

# Editor File Edit Function
def Ed_edit_date(request,id,pid):
    pid=pid
    id=id
    pide=request.session.get('uid')
    user=ED_User.objects.get(user=pide)
    if request.method=='POST':
        a7=request.POST.get('a7')
        a8=request.POST.get('a8')
        a9=request.POST.get('a9')
        a10=request.POST.get('a10')
        a11=request.POST.get('a11')
        a12=request.POST.get('a12')
        a13=request.POST.get('a13')
        a14=request.POST.get('a14')
        a15=request.POST.get('a15')
        a16=request.POST.get('a16')
        a17=request.POST.get('a17')
        a18=request.POST.get('a18')
        a19=request.POST.get('a19')
        a20=request.POST.get('a20')
        a21=request.POST.get('a21')
        a22=request.POST.get('a22')
        a23=request.POST.get('a23')
        a24=request.POST.get('a24')
        a25=request.POST.get('a25')
        a26=request.POST.get('a26')

        
        file_obj = Editor_push.objects.get(id=id)
        file = file_obj.qc_data.qc_file
        id=file_obj.id
        with open(f'{settings.BASE_DIR}//{file}', 'r') as f:
            data = json.load(f)
        data[pid]['KRIMA_status']=a7
        data[pid]['KRIMA_true_false']=a8
        data[pid]['KRIMA_type']=a9
        data[pid]['KRIMA_notes']=a10
        data[pid]['KRIMA_edited_gpt_person_or_business']=a11
        data[pid]['KRIMA_edited_gpt_company_check']=a12
        data[pid]['parent_company_name']=a13
        data[pid]['KRIMA_civil_penalty_validated']=a14
        data[pid]['KRIMA_civil_penalty_cleansed']=a15
        data[pid]['KRIMA_currency']=a16
        data[pid]['KRIMA_civil_penalty_usd']=a17
        data[pid]['KRIMA_disgorgement_restitution_usd']=a18
        data[pid]['KRIMA_imposed_penalty']=a19
        data[pid]['KRIMA_settled_value']=a20
        data[pid]['KRIMA_non_monetary_penalty']=a21
        data[pid]['Ok']=a22
        data[pid]['gpt_area_of_activity_or_service']=a23
        data[pid]['gpt_area_of_regulation']=a24
        data[pid]['KRIMA_area_of_activity_or_service']=a25
        data[pid]['KRIMA_area_of_regulation']=a26
        with open(f'{settings.BASE_DIR}//{file}', 'w') as f:
            json.dump(data,f)
        return redirect(f'/ed_view_file/{id}')
    else:
        file_obj = Editor_push.objects.get(id=id)
        file = file_obj.qc_data.qc_file
        id=file_obj.id
        with open(f'{settings.BASE_DIR}//{file}', 'r') as f:
            data = json.load(f)
        sr_no=data[pid]['sr_no']
        Article=data[pid]['Article']
        gpt=data[pid]['gpt_summary']
        Date=data[pid]['Date']
        Regulatory=data[pid]['Regulatory']
        Title=data[pid]['Title']
        URL=data[pid]['URL']
        KRIMA_status=data[pid]['KRIMA_status']
        KRIMA_true_false=data[pid]['KRIMA_true_false']
        KRIMA_type=data[pid]['KRIMA_type']
        KRIMA_notes=data[pid]['KRIMA_notes']
        KRIMA_edited_gpt_person_or_business=data[pid]['KRIMA_edited_gpt_person_or_business']
        KRIMA_edited_gpt_company_check=data[pid]['KRIMA_edited_gpt_company_check']
        parent_company_name=data[pid]['parent_company_name']
        KRIMA_civil_penalty_validated=data[pid]['KRIMA_civil_penalty_validated']
        KRIMA_civil_penalty_cleansed=data[pid]['KRIMA_civil_penalty_cleansed']
        KRIMA_currency=data[pid]['KRIMA_currency']
        KRIMA_civil_penalty_usd=data[pid]['KRIMA_civil_penalty_usd']
        KRIMA_disgorgement_restitution_usd=data[pid]['KRIMA_disgorgement_restitution_usd']
        KRIMA_imposed_penalty=data[pid]['KRIMA_imposed_penalty']
        KRIMA_settled_value=data[pid]['KRIMA_settled_value']
        KRIMA_non_monetary_penalty=data[pid]['KRIMA_non_monetary_penalty']
        ok=data[pid]['Ok']
        gpt_area_of_activity_or_service=data[pid]['gpt_area_of_activity_or_service']
        gpt_area_of_regulation=data[pid]['gpt_area_of_regulation']
        KRIMA_area_of_activity_or_service=data[pid]['KRIMA_area_of_activity_or_service']
        KRIMA_area_of_regulation=data[pid]['KRIMA_area_of_regulation']
    return render(request,'editior_temps/ed_edit.html',locals())

# Editor Apply Filetr Then Edit File Function
def Ed_filter_edit(request,id,pid):
    pide=request.session.get('uid')
    user=ED_User.objects.get(user=pide)
    file_obj = Editor_push.objects.get(id=id)
    file = file_obj.qc_data.qc_file
    id = file_obj.id
    data = request.session.get('data_re')
    if request.method == 'POST':
        fields = {
            'sr_no': 'a1',
            'Date': 'a2',
            'Regulatory': 'a3',
            'Title': 'a4',
            'KRIMA_status': 'a7',
            'KRIMA_true_false': 'a8',
            'KRIMA_type': 'a9',
            'KRIMA_notes': 'a10',
            'KRIMA_edited_gpt_person_or_business': 'a11',
            'KRIMA_edited_gpt_company_check': 'a12',
            'parent_company_name': 'a13',
            'KRIMA_civil_penalty_validated': 'a14',
            'KRIMA_civil_penalty_cleansed': 'a15',
            'KRIMA_currency': 'a16',
            'KRIMA_civil_penalty_usd': 'a17',
            'KRIMA_disgorgement_restitution_usd': 'a18',
            'KRIMA_imposed_penalty': 'a19',
            'KRIMA_settled_value': 'a20',
            'KRIMA_non_monetary_penalty': 'a21',
            'Ok':'a22',
            'gpt_area_of_activity_or_service':'a23',
            'gpt_area_of_regulation':'a24',
            'KRIMA_area_of_activity_or_service':'a25',
            'KRIMA_area_of_regulation':'a26',
        }
         # Load the JSON file
        with open(f'{settings.BASE_DIR}/{file}', 'r') as f:
            data1 = json.load(f)

        # Find the index where the sr_no matches
        for index, item in enumerate(data1):
            if item['sr_no'] == data[pid]['sr_no']:
                # Update only the fields specified in the fields dictionary
                for field, key in fields.items():
                    item[field] = request.POST.get(key)
                data1[index] = item
                data[pid]=data1[index]
                dt=data[pid]
        data[pid]=dt
        # Save the updated data to the JSON file
        with open(f'{settings.BASE_DIR}/{file}', 'w') as f:
            json.dump(data1, f)
        da={'data':data,'id':id}
        return render(request,'editior_temps/ed_filter.html',da)
    else:
        uid=pid
        context = {
            'sr_no': data[pid]['sr_no'],
            'Article': data[pid]['Article'],
            'Date': data[pid]['Date'],
            'Regulatory': data[pid]['Regulatory'],
            'Title': data[pid]['Title'],
            'URL': data[pid]['URL'],
            'KRIMA_status': data[pid]['KRIMA_status'],
            'KRIMA_true_false': data[pid]['KRIMA_true_false'],
            'KRIMA_type': data[pid]['KRIMA_type'],
            'KRIMA_notes': data[pid]['KRIMA_notes'],
            'KRIMA_edited_gpt_person_or_business': data[pid]['KRIMA_edited_gpt_person_or_business'],
            'KRIMA_edited_gpt_company_check': data[pid]['KRIMA_edited_gpt_company_check'],
            'parent_company_name': data[pid]['parent_company_name'],
            'KRIMA_civil_penalty_validated': data[pid]['KRIMA_civil_penalty_validated'],
            'KRIMA_civil_penalty_cleansed': data[pid]['KRIMA_civil_penalty_cleansed'],
            'KRIMA_currency': data[pid]['KRIMA_currency'],
            'KRIMA_civil_penalty_usd': data[pid]['KRIMA_civil_penalty_usd'],
            'KRIMA_disgorgement_restitution_usd': data[pid]['KRIMA_disgorgement_restitution_usd'],
            'KRIMA_imposed_penalty': data[pid]['KRIMA_imposed_penalty'],
            'KRIMA_settled_value': data[pid]['KRIMA_settled_value'],
            'KRIMA_non_monetary_penalty': data[pid]['KRIMA_non_monetary_penalty'],
            'ok':data[pid]['Ok'],
            'pid':uid,
            'id':id,
            'gpt_area_of_activity_or_service':data[pid]['gpt_area_of_activity_or_service'],
            'gpt_area_of_regulation':data[pid]['gpt_area_of_regulation'],
            'KRIMA_area_of_activity_or_service':data[pid]['KRIMA_area_of_activity_or_service'],
            'KRIMA_area_of_regulation':data[pid]['KRIMA_area_of_regulation'],
            'gpt':data[pid]['gpt_summary']
          
        }
        return render(request,'editior_temps/ed_edit.html',context)
    
# Final File send To Admin Function
def Ed_Send_file(request,id):
    uid=request.session.get('uid')
    u=Editor_push.objects.get(id=id) 
    user=User.objects.get(id=uid)
    ed=ED_User.objects.get(user=user)
    pd=Final_data_PM()
    pd.Editior=ed
    pd.Edited_file=u
    pd.save()
    u.sta=True
    u.save()
    return redirect('/ed_home')

# Final File Show on Page Function
def Ed_record(request):
    qc_data=Final_data_PM.objects.all()   
    user=request.user
    data={'data':qc_data}

    return render(request,'admin_temps/ed_record.html',data)


# Final File Download Function
def Download(request,id):
    files = ''
    name = ''
    fd = Final_data_PM.objects.filter(id=id)
    for i in fd:
        files = i.Edited_file.qc_data.qc_file
        name = i.Edited_file.qc_data.qc_file.name
    data = []
    with open(files.path, 'r') as f:
        f1 = json.load(f)
    for i in f1:
        del i["GPT_Description_Automated"]
        del i['parent_company_name']
        del i['Ok']
        del i['method']
        data.append(i)
    # Create a JSON response
    response = HttpResponse(json.dumps(data), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(name)}.json"'
    return response

# About 
def About(request):
    return render(request,'admin_temps/about.html')

# Feature
def Feature(request):
    return render(request,'admin_temps/feature.html')


# def Delete_user(request,id):
    
#         qc_user=Qc_user.objects.get(id=id)
#         qc_user.delete()
#         return redirect('/all_user')
#     # except:
#     #     return redirect('/dashboard')