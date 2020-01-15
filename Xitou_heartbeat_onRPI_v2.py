
# coding: utf-8
import PyQt5
import requests
import urllib.request
import re
import os 
import pandas as pd
from datetime import datetime, timedelta
from time import gmtime, strftime
import numpy as np
import shutil
import fileinput

def query_data_XT(arg1):
    try:
        date = datetime.now().strftime("%Y%m")
        url = 'http://ec2-54-175-179-28.compute-1.amazonaws.com/get_csv_xitou.php?device_id='+str(arg1)+'&year_month='+str(date)
        # print("url:" + url)
        # Get the URL of the csv file
        csv_LINK_PATTERN = 'href="(.*)">Download'
        req  = urllib.request.Request(url)
        html = urllib.request.urlopen(req)
        doc  = html.read().decode('utf8')

        string1 = "'>Download ID" + str(arg1) + str(date) +" Data</a><br>"
        get_rul_patten = doc.strip(string1).strip("<a href='")
        file_name      = str(arg1) + "_csvFid"
        server_path    = "http://ec2-54-175-179-28.compute-1.amazonaws.com/"+ get_rul_patten

        # Creat the folder to save the csv file
        if not os.path.exists('./'+ file_name):
            os.makedirs('./'+ file_name)
        urllib.request.urlretrieve(server_path,'./'+file_name+'/'+file_name+'.csv')

        # Create a dataframe from the URL by data crawling
        local_csv_pos = './'+file_name+'/'+file_name+'.csv'
        
        # perform a preprocessing of csv file
        with open(local_csv_pos,'r') as f:
            global data_fir_line
            data_fir_line=len(f.readline())
            # print(data_fir_line)
        if data_fir_line < 230:
            for line in fileinput.input(local_csv_pos, inplace=1):
                if not fileinput.isfirstline():
                    print(line.replace('\n',''))
                    
        del_col = [0,2,4,6,8]
        csv_data = pd.read_csv(local_csv_pos,sep=", |,, | = |= ", header=None, index_col=False, engine='python')
        csv_data.drop(del_col, axis=1, inplace = True)

        colName = ['id', 'time', 'weather', 'air', 'acceleration']
        csv_data.columns = colName # weather column (溫度、大氣壓力、濕度、風速、風向、雨量)

        last_uploadTime = csv_data.time[len(csv_data.time) - 1]
        last_uploadTime = pd.to_datetime(last_uploadTime, format="%Y%m%d%H%M%S")
        localTimeStamp  = pd.to_datetime(strftime("%Y%m%d%H%M%S"), format="%Y%m%d%H%M%S")

        deltaT = localTimeStamp - last_uploadTime
        alrTimeIntv = timedelta(minutes = 15)

        if deltaT > alrTimeIntv:
            deltaDay = deltaT.days
            deltaHr  = deltaT.seconds // 3600
            deltaMin = (deltaT.seconds % 3600) // 60
            deltaSec = deltaT.seconds % 60
            outputStr = "Offline time: {} day, {} hr, {} min".format(deltaDay,deltaHr,deltaMin)
        else:
            outputStr = "Online"
    except:
        outputStr = "No data received this month"
    
    return outputStr   

saveFid  = []
idNumDict  = [{'name':'鳳凰茶園','id':'4008'},
              {'name':'武岫農圃','id':'4005'},
              {'name':'溪頭活動','id':'4007'},
              {'name':'溪頭辦公','id':'4002'},
              {'name':'溪頭苗園','id':'4003'},
              {'name':'內湖國小','id':'4004'},
              {'name':'神    木','id':'4006'},
              {'name':'米堤飯店','id':'4010'},
              {'name':'天 文 台','id':'4011'},
              {'name':'杉林溪飯','id':'4012'},
              {'name':'竹山本部','id':'4001'},
              {'name':'下坪植物','id':'4009'}]
# idNumDict  = [{'name':'天 文 台','id':'4011'}]

DBName = 'Xitou'

flag = 0
for ii in range(0, len(idNumDict)):       
    writingStr = query_data_XT(idNumDict[ii]["id"])
    now = strftime("%Y%m%d%H%M")
    if (ii == 0):
        queryFid = "{}_{}_hearbeatList.txt".format(now, DBName)
        saveFid  += [queryFid]

    if (flag == 0):
        with open(queryFid, "a") as file:
            file.write("---------------Device heartbeat---------------")
            file.write("\n")
            file.write("Name of project: " + DBName)
            file.write("\n")
            file.write("Query time: {}".format(strftime("%Y/%m/%d %H:%M")))
            file.write("\n")
            flag = 1   
    with open(queryFid, "a") as file:
        writing = "{}    {}    {}".format(idNumDict[ii]["name"],idNumDict[ii]["id"],writingStr)
        file.write(writing)
        file.write("\n")
    print(str(idNumDict[ii]["id"]) + "  Done.")


smtpssl=smtplib.SMTP_SSL("smtp.gmail.com", 465)
smtpssl.ehlo()
smtpssl.login("n86024042@gmail.com", "ibovbvqwpobuofqb")

msg = ""
for ii in range(0, len(saveFid)):    
    with open(saveFid[ii],'r') as file:
        msg += file.read()       
        
mime = MIMEText(msg, "plain", "utf-8")
mime["Subject"] = "Icebergtek Device heartbeat in Xitou\n"
msgEmail        = mime.as_string()  

# to_addr  = ["ian@icebergtek.com",
#             "odie@icebergtek.com",
#             "white@icebergtek.com",
#             "jim@icebergtek.com",
#             "weichiang@ntu.edu.tw",
#             "james.wang@icebergtek.com"]

to_addr  = ["ian@icebergtek.com"]
          

status = smtpssl.sendmail("n86024042@gmail.com", 
                          to_addr, 
                          msgEmail)
if status == {}:
    print("Sending e-mail is done.")
    smtpssl.quit()
else:
    print("Failed to transmit.")
    smtpssl.quit()

