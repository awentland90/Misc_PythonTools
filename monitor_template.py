import psutil
import datetime
from apscheduler.scheduler import Scheduler
from subprocess import call
import smtplib
import subprocess
from email.mime.text import MIMEText
import getpass

'''
Program: Linux Process Monitor
========================================================================================================================

Created by: Andy Wentland, 2016
Version: 1.0
Purpose: Monitor Linux processes via email updates
Notes:
    1. There are a few Python modules you need to have installed - see import area above
    2. Currently the email smtp works with GMAIL. If using another email host, you will need to update the smtp info in send_email() function
    3. You must run this script on the computer where the processes are running.
    4. Process name can be found using 'top' command in Linux once process in running
    5. This program will continue to run until the process ends or you terminate this program.
    6. You will need to enter your GMAIL username/password in this program. There are libraries/methods to hide this but for simplicity
       they are out in the open in this example so please be careful or use dummy account!


Example - using the top command you should see something like this:

    PID   USER      PR  NI VIRT  RES  SHR  S %CPU  %MEM TIME+     COMMAND
    22634 user1     20   0 3893m 1.6g 8088 R 199.5  1.7 111:33.57 SIMULATIONv5.0
    22637 user1     20   0 4159m 1.6g 9012 R 199.5  1.7 111:32.74 SIMULATIONv5.0
    22639 user1     20   0 5010m 1.7g  11m R 199.5  1.8 111:31.04 SIMULATIONv5.0

    So you will set your process_name variable to be 'SIMULATIONv5.0'

========================================================================================================================
'''


# ----- Begin Default User Input ----- #


run_name = "SIMULATIONv5.0_Run1"  # Unique name for this run

# How often do you want updates?
# Only once: interval = 'None'
# Once a minute: interval = 'Minute'
# Once an hour: interval = 'Hour',
# 4 times a day: interval = '4Day'
# Once a day: interval = '1Day'
interval = '4Day'

# Computer name currently running the process
machine = "linux_machine3"

# Look up processes based on name (can be found using top, see example above)
process_name = 'SIMULATIONv5.0'

# Directory where output is going
out_dir = '/linux_machine3/simulation_output/'

# Log file name
log_file = "log_%s.txt" % run_name

#Email Info

fromaddr = 'gmail_username@gmail.com'
toaddrs = 'gmail_username@gmail.com'

username = 'gmail_username'
password = 'gmail_password'


# ----- End Default User Input ----- #

# Clean up/create log file
call(["rm", log_file])
call(["touch", log_file])

def send_email():
        # Read Log file and email to yourself
        fp = open(log_file, 'r')
        msg = MIMEText("\n".join(fp.read().strip().split("\n")[-15:]))
        fp.close()
        server = smtplib.SMTP('smtp.gmail.com:587') # SMTP address, default is GMAIL
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddrs, msg.as_string())
        server.quit()

def check_run():
        # Check if program is running, output sys info to log file
        proc_var = []
        time_now = str(datetime.datetime.now())
        try:
            space_now = subprocess.check_output(["df", "-h", out_dir])
        except subprocess.CalledProcessError as e:
            space_now = "Drive not mounted"
        run_on = "No"
        for proc in psutil.process_iter():
            process = psutil.Process(proc.pid)  # Get the process info using PID
            pname = process.name()  # Here is the process name
            if pname.startswith(process_name):
                run_on = 'Yes'
                proc_var.append(pname)
        with open(log_file, "w") as text_file:
            if run_on == 'Yes':
                text_file.write("Job:            %s \n" % run_name)
                text_file.write("Machine:    %s\n" % machine)
                text_file.write("Time:          %s\n" % time_now)
                text_file.write("Processes Running:\n %s\n" % proc_var)
                text_file.write(" ")
                text_file.write("Out Directory:\n %s\n" % space_now)
                text_file.write(" ")
            else:
                text_file.write("PROCESSES NOT ON! \n")
                text_file.write("Job: %s \n" % run_name)
                text_file.write("Out Directory:\n %s\n" % space_now)
		text_file.close()
		send_email()
                sched.shutdown(wait=False)
        text_file.close()
        send_email()


# ----- Define Possible Time Intervals To Send Email Notifications ----- #

if interval == 'None':
    # Send email only once
    sched = Scheduler()
    check_run()
elif interval == 'Minute':
    # Send email once a minute
    sched = Scheduler()
    sched.daemonic = False
    sched.start()
    sched.add_interval_job(check_run, minutes=1)
elif interval == 'Hour':
    # Send email once an hour
    sched = Scheduler()
    sched.daemonic = False
    sched.start()
    sched.add_interval_job(check_run, hours=1)
elif interval == 'Day':
    # Send email once a day
    sched = Scheduler()
    sched.daemonic = False
    sched.start()
    sched.add_interval_job(check_run, days=1)
elif interval == '4Day':
    # Send email 4 times a day
    sched = Scheduler()
    sched.daemonic = False
    sched.start()
    sched.add_interval_job(check_run, hours=6)
else:
    print("Please choose a correct interval for email delivery. Current interval %s not programmed" % interval)
