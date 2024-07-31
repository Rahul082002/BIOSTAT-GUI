# Code for desktop app for CG-STAT

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import paramiko
import io
import threading
import sys
from PIL import Image, ImageTk
import cv2
import os

global hostname,username,password,port,raw_file_name,screen_width,screen_height
hostname = ""
port=22
username = ""
password = ""
raw_file_name=""

def update_video(label, vid):
    ret, frame = vid.read()
    if not ret:
        vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = vid.read()
    
    if ret:

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(img)
        label.img = img  
        label.config(image=img)
    label.after(5, update_video, label, vid)  

def center_window(root, width, height):
    global screen_width,screen_height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f'{width}x{height}+{x}+{y}')
    root.wm_state('zoomed')

def create_labeled_image_process(parent, photo1,photo2,photo3):
    frame = Frame(parent,bg="white")
    label1 = Label(frame, image=photo1,bg="white")
    label2 = Label(frame, image=photo2,bg="white")
    label3 = Label(frame, image=photo3,bg="white")
    label1.pack(side='left', padx=(0, 0))
    label2.pack(side='left', padx=(0, 0))
    label3.pack(side='left', padx=(0, 0))
    frame.pack(pady=10)

def new_file(root):

    for widget in root.winfo_children():
        widget.destroy()
    my_menu=Menu(root)
    my_menu.config(activebackground="blue", activeforeground="black",font=('Helvetica',12))
    file_menu=Menu(my_menu,tearoff=0)
    my_menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Open",command=lambda:open_file(root))
    file_menu.add_command(label="New",command=lambda:new_file(root))
    file_menu.add_separator()
    file_menu.add_command(label="Exit",command=root.quit)
    file_menu.config(bg="white", fg="black", activebackground="lightblue", activeforeground="black",font=('Helvetica', 12))
    root.config(menu=my_menu)
    image_path =  "Images\\Bg3.png" # Replace with your image path
    image4 = Image.open(image_path)
    image4 = image4.resize((screen_width,screen_height), Image.LANCZOS)
    photo4 = ImageTk.PhotoImage(image4)
    canvas = Canvas(root, width=photo4.width(), height=photo4.height())
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=photo4, anchor='nw')
    bg_label = Label(root, image=photo4)
    bg_label.place(relwidth=1, relheight=1)
    
    bg_frame = Frame(root,bg="white")
  
    bg_frame.place(relx=0.7, rely=0.1, relwidth=0.28,relheight=0.55)
 
    image1 = Image.open("Images\\Cdac_logo.png")  # Replace with your image path
    image2 = Image.open("Images\\institute_logo.png")  # Replace with your image path
    image3 = Image.open("Images\\logo.png")
   
    image1 = image1.resize((120, 75), Image.LANCZOS)
    image2 = image2.resize((120, 75), Image.LANCZOS)
    image3 = image3.resize((120, 75), Image.LANCZOS)
   
    photo1 = ImageTk.PhotoImage(image1)
    photo2 = ImageTk.PhotoImage(image2)
    photo3 = ImageTk.PhotoImage(image3)

    create_labeled_image_process(bg_frame,photo1,photo2,photo3)
    Label(bg_frame, text="Test ID:",bg="white",font=('Helvetica',14, 'bold')).pack(pady=10)
    entry = Entry(bg_frame,bg="white",font=('Helvetica', 12))
    entry.pack(pady=10)
    
    Label(bg_frame, text="Select Technique:",bg="white",font=('Helvetica', 14, 'bold')).pack(pady=10)
    option_var=["dpv","cv"]
    style = ttk.Style()
    style.configure('TCombobox',fieldbackground='#4caf50',background='white',foreground='#4caf50')
    process=ttk.Combobox(bg_frame,values=option_var,state="readonly",font=('Helvetica', 12),style='TCombobox')
    process.pack(pady=10)
    Button(bg_frame, text="OK",bg="#3572b9",fg="white",font=('Helvetica', 12,'bold') ,command=lambda:create_file(process,entry)).pack(pady=20)
    root.photo1 = photo1
    root.photo2 = photo2
    root.photo3 = photo3
    root.photo4=photo4

def create_file(process,entry):
    global raw_file_name
    process_value=process.get()
    entry_value=entry.get()
    file_path_process="/home/pi/dpv/data/process"
    file_path="/home/pi/dpv/data/file_name"
    raw_file_name=entry_value
    file_name_path=f"/home/pi/dpv/experiment/{raw_file_name}"
    flag=True

    try:
       
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the Raspberry Pi
        ssh.connect(hostname, port, username, password)
        print("Connected to Raspberry Pi")

        # Use SFTP to create and write to the file
        sftp = ssh.open_sftp()
        
        try:
            with sftp.file(file_path_process, 'w') as file:
                if(process_value=="cv"):
                    print("NPV")
                    file.write("NPV")
                else:
                    file.write("NPD")
                    print("NPD")
                print(f"Created or rewrote content to {file_path_process}")
            with sftp.file(file_path, 'w') as file:
                file.write(entry_value)
                print("changed name")

            stdin, stdout, stderr = ssh.exec_command(f'if [ -f "{file_name_path}" ]; then echo "File exists"; else echo "File does not exist"; fi')
            output = stdout.read().decode().strip()

        
        
            ssh.close()
        finally:
            sftp.close()

       
            if output == "File exists":
             flag=True
            else:
                flag=False

        
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        ssh.close()
        print("SSH connection closed")

    if (flag==False):
        create_menu(root,process_value,raw_file_name)
    elif(flag==True):
        messagebox.showerror("Error", "File name already exists")
        new_file(root)
    else:
        print("error")

def create_labeled_image_open(parent, photo1,photo2,photo3):
    frame = Frame(parent,bg="white")
    label1 = Label(frame, image=photo1,bg="white")
    label2 = Label(frame, image=photo2,bg="white")
    label3 = Label(frame, image=photo3,bg="white")
    label1.pack(side='left', padx=(0, 0))
    label2.pack(side='left', padx=(0, 0))
    label3.pack(side='left', padx=(0, 0))
    frame.pack(pady=10)
    
def open_file(root):
    for widget in root.winfo_children():
        widget.destroy()
    my_menu=Menu(root)
    my_menu.config(activebackground="blue", activeforeground="black",font=('Helvetica', 12))
    file_menu=Menu(my_menu,tearoff=0)
    my_menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Open",command=lambda:open_file(root))
    file_menu.add_command(label="New",command=lambda:new_file(root))
    file_menu.add_separator()
    file_menu.add_command(label="Exit",command=root.quit)
    file_menu.config(bg="white", fg="black", activebackground="lightblue", activeforeground="black",font=('Helvetica', 12))
    root.config(menu=my_menu)
    image_path =  "Images\\Bg4.png" # Replace with your image path
    image4 = Image.open(image_path)
    image4 = image4.resize((screen_width,screen_height), Image.LANCZOS)
    photo4 = ImageTk.PhotoImage(image4)
    canvas = Canvas(root, width=photo4.width(), height=photo4.height())
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=photo4, anchor='nw')
    bg_label = Label(root, image=photo4)
    bg_label.place(relwidth=1, relheight=1)
    
    bg_frame = Frame(root,bg="white")
    bg_frame.place(relx=0.7, rely=0.1, relwidth=0.28,relheight=0.6)
    image1 = Image.open("Images\\Cdac_logo.png")  # Replace with your image path
    image2 = Image.open("Images\\institute_logo.png")  # Replace with your image path
    image3 = Image.open("Images\\logo.png")
    image1 = image1.resize((120, 75), Image.LANCZOS)
    image2 = image2.resize((120, 75), Image.LANCZOS)
    image3 = image3.resize((120, 75), Image.LANCZOS)
  
    photo1 = ImageTk.PhotoImage(image1)
    photo2 = ImageTk.PhotoImage(image2)
    photo3 = ImageTk.PhotoImage(image3)

    create_labeled_image_open(bg_frame,photo1,photo2,photo3)
    Label(bg_frame, text="Select Test ID",font=('Helvetica', 22, 'bold'),bg="white").pack(pady=10)
    Label(bg_frame, text="Test ID:",font=('Helvetica',16),bg="white").pack(pady=10)
    entry = Entry(bg_frame,bg="white",font=('Helvetica',16))
    entry.pack(pady=10)
    Button(bg_frame, text="Open", command=lambda:view_file(entry),fg="white",bg="#3572b9",font=('Helvetica',16,'bold')).pack(pady=20)
    root.photo1 = photo1
    root.photo2 = photo2
    root.photo3 = photo3
    root.photo4=photo4

def create_menu(root,process_value,raw_file_name):
    for widget in root.winfo_children():
        widget.destroy()
    my_menu=Menu(root)
    my_menu.config(activebackground="blue", activeforeground="black",font=('Helvetica', 12))
    file_menu=Menu(my_menu,tearoff=0)
    my_menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Open",command=lambda:open_file(root))
    file_menu.add_command(label="New",command=lambda:new_file(root))
    file_menu.add_separator()
    file_menu.add_command(label="Exit",command=root.quit)
    file_menu.config(bg="white", fg="black", activebackground="lightblue", activeforeground="black",font=('Helvetica', 12))
    root.config(menu=my_menu)
    if (process_value=='cv'):
        cv(raw_file_name)
    else:
        dpv(raw_file_name)


def view_file(entry):
    entry_value=entry.get()
    remote_file_path = f'/home/pi/dpv/Graphs/{entry_value}.png'  # Replace with the path to your image file on the Raspberry Pi
    local_file_path = f"Graphs\\{entry_value}.png"  # Path to save the retrieved image on your desktop
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)
    sftp = ssh.open_sftp()
    try:
        sftp.get(remote_file_path, local_file_path)
    except:
       messagebox.showerror("Error", "File name doesn't exist")
    finally:
        sftp.close()
    ssh.close()
    image = Image.open(local_file_path)
    image.show()
    
def create_labeled_entry(parent,text, unit_text):
    frame = Frame(parent,bg="white")
    entry = Entry(frame,font=('Helvetica', 12))
    text_label=Label(frame, text=text,bg="white",font=('Helvetica', 12))
    text_label.pack(side='left',padx=(5,0))
    unit_label = Label(frame, text=unit_text,bg="white",font=('Helvetica', 12))
    entry.pack(side='left', padx=(5, 0))
    unit_label.pack(side='left', padx=(5, 0))
    frame.pack(pady=10)
    return entry

def create_labeled_image(parent, photo1,photo2,photo3):
    frame = Frame(parent,bg="white")
    label1 = Label(frame, image=photo1,bg="white")
    label2 = Label(frame, image=photo2,bg="white")
    label3 = Label(frame, image=photo3,bg="white")
    label1.pack(side='left', padx=(5, 0))
    label2.pack(side='left', padx=(5, 0))
    label3.pack(side='left', padx=(5, 0))
    frame.pack(pady=10)
    

def dpv(raw_file_name):
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    image_path = "Images\\Bg2.png"  # Replace with your image path
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((screen_width,screen_height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    canvas = Canvas(root, width=bg_photo.width(), height=bg_photo.height())
    canvas.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=(N, S, W, E))
    canvas.create_image(0, 0, image=bg_photo, anchor='nw')
    
    options_frame = Frame(root, padx=10, pady=10, bg='white')
    canvas.create_window(10, 10, anchor='nw', window=options_frame)

    plot_frame = Frame(root, padx=10, pady=10,bg="black")
    canvas.create_window(bg_photo.width()//2.75,bg_photo.height()//6,anchor='nw', window=plot_frame)

    image1 = Image.open("Images\\cdac_logo.png")  # Replace with your image path
    image2 = Image.open("Images\\institute_logo.png")  # Replace with your image path
    image3 = Image.open("Images\\logo.png")
       
    image1 = image1.resize((120, 75), Image.LANCZOS)
    image2 = image2.resize((120, 75), Image.LANCZOS)
    image3 = image3.resize((120, 75), Image.LANCZOS)
    photo1 = ImageTk.PhotoImage(image1)
    photo2 = ImageTk.PhotoImage(image2)
    photo3 = ImageTk.PhotoImage(image3)

    create_labeled_image(options_frame,photo1,photo2,photo3)
    Label(options_frame,text="Differential Pulse Voltammetry (DPV)",font=('Helvetica', 18, 'bold'),bg="white").pack(pady=0)
    initial_potential = create_labeled_entry(options_frame,"Initial Potential:","V")
    final_potential = create_labeled_entry(options_frame,"  Final Potential:","V")
    pulse_amplitude = create_labeled_entry(options_frame,"  Pulse Amplitude:", "V")
    pulse_duration = create_labeled_entry(options_frame,"    Pulse Duration:", "\u03BCs")
    pulse_period = create_labeled_entry(options_frame,"       Pulse Period:","\u03BCs")
    quite_time = create_labeled_entry(options_frame,"      Quite Time:","s")
    step_size = create_labeled_entry(options_frame,"    Enter Step Size:", "V")

    start_button = Button(options_frame, text="Run",bg="#3572b9", fg="white",font=('Helvetica', 12) ,command=lambda:label_create_dpv(root,plot_frame,initial_potential,final_potential,pulse_amplitude,pulse_duration,pulse_period,quite_time,step_size,options_frame,raw_file_name))
    start_button.pack(pady=0)
    root.photo1 = photo1
    root.photo2 = photo2
    root.photo3 = photo3
    root.bg_photo = bg_photo

    
def cv(raw_file_name):
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    image_path = "Images\\Bg1.png"  # Replace with your image path
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((screen_width,screen_height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    canvas = Canvas(root, width=bg_photo.width(), height=bg_photo.height())
    canvas.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=(N, S, W, E))
    canvas.create_image(0, 0, image=bg_photo, anchor='nw')
   
    options_frame = Frame(root, padx=10, pady=10, bg='white')
    canvas.create_window(10, 10, anchor='nw', window=options_frame)

    plot_frame = Frame(root, padx=10, pady=10,bg="black")
    canvas.create_window(bg_photo.width()//2.75,bg_photo.height()//6,anchor='nw', window=plot_frame)

    image1 = Image.open("Images\\cdac_logo.png")  # Replace with your image path
    image2 = Image.open("Images\\institute_logo.png")  # Replace with your image path
    image3 = Image.open("Images\\logo.png")

    image1 = image1.resize((120, 75), Image.LANCZOS)
    image2 = image2.resize((120, 75), Image.LANCZOS)
    image3 = image3.resize((120, 75), Image.LANCZOS)
 
    photo1 = ImageTk.PhotoImage(image1)
    photo2 = ImageTk.PhotoImage(image2)
    photo3 = ImageTk.PhotoImage(image3)
    
    create_labeled_image(options_frame,photo1,photo2,photo3)
    Label(options_frame,text="Cyclic Voltammetry (CV)",font=('Helvetica', 18, 'bold'),bg="white").pack(pady=0)
    min_potential= create_labeled_entry(options_frame,"Minimum Potential:","V")
    max_potential= create_labeled_entry(options_frame,"Maximum Potential:","V")
    start_potential= create_labeled_entry(options_frame,"          Start Potential:","V")
    step_potential= create_labeled_entry(options_frame,"          Step Potential:","V")
    total_cycle= create_labeled_entry(options_frame,"             Total cycles:"," ")
    time_interval=  create_labeled_entry(options_frame,"              Time Interval:","ms")
    
    start_button = Button(options_frame, text="Run",font=('Helvetica', 12),bg="#3572b9", fg="white", command=lambda:label_create_cv(root,plot_frame,min_potential,max_potential,start_potential,step_potential,total_cycle,time_interval,options_frame,raw_file_name))
    start_button.pack(pady=5)
    root.photo1 = photo1
    root.photo2 = photo2
    root.photo3 = photo3
    root.bg_photo = bg_photo


def label_create_cv(root,plot_frame,min_potential,max_potential,start_potential,step_potential,total_cycle,time_interval,options_frame,raw_file_name):
    analysing=Label(options_frame, text="Analysing...",fg="#3572b9",bg="white",font=('Helvetica', 12,'bold'))
    analysing.pack(pady=10)
    on_start_button_click_cv(root,plot_frame,min_potential,max_potential,start_potential,step_potential,total_cycle,time_interval,options_frame,raw_file_name,analysing)

def label_create_dpv(root,plot_frame,initial_potential,final_potential,pulse_amplitude,pulse_duration,pulse_period,quite_time,step_size,options_frame,raw_file_name):
    analysing=Label(options_frame, text="Analysing...",fg="#3572b9",bg="white",font=('Helvetica', 12,'bold'))
    analysing.pack(pady=10)
    on_start_button_click_dpv(root,plot_frame,initial_potential,final_potential,pulse_amplitude,pulse_duration,pulse_period,quite_time,step_size,options_frame,raw_file_name,analysing)

def on_click(root,process,entry):
    create_menu(root)
    create_file(process,entry)

def on_plot_button_click(plot_frame,raw_file_name,options_frame):
     
    data_file_path = f"/home/pi/dpv/experiment/{raw_file_name}"
   
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)

    sftp = ssh.open_sftp()
    try:
        with sftp.open(data_file_path, 'r') as remote_file:
            file_content = remote_file.read()
    except Exception as e:
        print(f"Error reading remote file: {e}")
        return
    finally:
        sftp.close()
        ssh.close()

    try:
  
        data = np.loadtxt(io.StringIO(file_content.decode('utf-8')), delimiter='\t')  # Adjust delimiter if needed

        x = data[:, 0]
        y = data[:, 1]

        fig, ax = plt.subplots()
        ax.scatter(x, y, color='b', label='Data')
        ax.set_xlabel('Potential (V)')
        ax.set_ylabel('Current (A)')
        ax.set_title('Graph of Potential vs Current')
        ax.legend()

        for widget in plot_frame.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        print("Plot created successfully!")
    except Exception as e:
        print(f"Error plotting data: {e}")
    
    smooth_button = Button(options_frame, text="Smooth",bg="#3572b9", fg="white",font=('Helvetica', 12), command=lambda:smooth_plot(fig,ax,options_frame,plot_frame,x,y))
    smooth_button.pack(pady=5)
    save_button = Button(options_frame, text="Save",bg="#3572b9", fg="white",font=('Helvetica', 12), command=lambda:save_plot(fig))
    save_button.pack(pady=5)

def smooth_plot(fig,ax,options_frame,plot_frame,x,y):
    ax.clear()
    window_size = 10 
    y_smooth=np.convolve(y, np.ones(window_size)/window_size, mode='valid')
    x_smooth = x[(window_size - 1)//2 : -(window_size - 1)//2]
    ax.plot(x_smooth, y_smooth, 'r-', label='Smoothed data')

    ax.set_xlabel('Potential (V)')
    ax.set_ylabel('Current (A)')
    ax.set_title('Graph of Potential vs Current')
    ax.legend()

    for widget in plot_frame.winfo_children():
            widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=BOTH, expand=1)
    print("Smoothed successfully!")
    
    

def save_plot(fig):
    try:
        local_file = f"Graphs\\{raw_file_name}.png"  # Path to the file on your desktop
        remote_file = f'/home/pi/dpv/Graphs/{raw_file_name}.png'  # Destination path on Raspberry Pi
        fig.savefig(local_file)  
        print("Plot saved as scatter_plot.png")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname, port, username, password)

        sftp = ssh.open_sftp()
        sftp.put(local_file, remote_file)  
        sftp.close()  
        ssh.close()   
        print(f"Successfully transferred {local_file} to {remote_file}")
        messagebox.showinfo("CG-STAT", "Plot saved successfully")
        if os.path.exists(local_file):
            os.remove(local_file)
            print(f"Deleted local file {local_file}")
        else:
            print(f"Local file {local_file} does not exist")

        
    except Exception as e:
        print(f"Error saving plot: {e}")
    
   
def on_start_button_click_dpv(root,plot_frame,initial_potential,final_potential,pulse_amplitude,pulse_duration,pulse_period,quite_time,step_size,options_frame,raw_file_name,analysing):
    initial_potential_value=initial_potential.get()
    final_potential_value=final_potential.get()
    pulse_amplitude_value=pulse_amplitude.get()
    pulse_duration_value=pulse_duration.get()
    pulse_period_value=pulse_period.get()
    quite_time_value=quite_time.get()
    step_size_value=step_size.get()
    file_path_initial_potential="/home/pi/dpv/data/dpv_initial_potential"
    file_path_final_potential="/home/pi/dpv/data/dpv_final_potential"
    file_path_pulse_amplitude="/home/pi/dpv/data/dpv_pulse_amplitude"
    file_path_pulse_duartion="/home/pi/dpv/data/dpv_pulse_duration"
    file_path_pulse_period="/home/pi/dpv/data/dpv_pulse_period"
    file_path_quite_time="/home/pi/dpv/data/dpv_quite_time"
    file_path_step_size="/home/pi/dpv/data/dpv_step_size"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname, port, username, password)
        print("Connected to Raspberry Pi")

        sftp = ssh.open_sftp()

        try:
            # Open the file in write mode (this will create the file if it does not exist)
            with sftp.file(file_path_initial_potential, 'w') as file:
                file.write(initial_potential_value)
            with sftp.file(file_path_final_potential, 'w') as file:
                file.write(final_potential_value)
            with sftp.file(file_path_pulse_amplitude, 'w') as file:
                file.write(pulse_amplitude_value)
            with sftp.file(file_path_pulse_duartion, 'w') as file:
                file.write(pulse_duration_value)
            with sftp.file(file_path_pulse_period, 'w') as file:
                file.write(pulse_period_value)
            with sftp.file(file_path_quite_time, 'w') as file:
                file.write(quite_time_value)
            with sftp.file(file_path_step_size, 'w') as file:
                file.write(step_size_value)
                

        finally:
            sftp.close()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        ssh.close()
        print("SSH connection closed")
    
    threading.Thread(target=execute_code, args=(analysing,options_frame,plot_frame,raw_file_name)).start()
    

def on_start_button_click_cv(root,plot_frame,min_potential,max_potential,start_potential,step_potential,total_cycle,time_interval,options_frame,raw_file_name,analysing):
    min_potential_value=min_potential.get()
    max_potential_value=max_potential.get()
    start_potential_value=start_potential.get()
    step_potential_value=step_potential.get()
    total_cycle_value=total_cycle.get()
    time_interval_value=time_interval.get()
    file_path_min_potential="/home/pi/dpv/data/cv_minimum_potential"
    file_path_max_potential="/home/pi/dpv/data/cv_maximum_potential"
    file_path_start_potential="/home/pi/dpv/data/cv_start_potential"
    file_path_step_potential="/home/pi/dpv/data/cv_step_potential"
    file_path_total_cycle="/home/pi/dpv/data/cv_total_cycle"
    file_path_time_interval="/home/pi/dpv/data/cv_time_interval"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname, port, username, password)
        print("Connected to Raspberry Pi")

        sftp = ssh.open_sftp()

        try:
         
            with sftp.file(file_path_min_potential, 'w') as file:
                file.write(min_potential_value)
                print(min_potential_value)
            with sftp.file(file_path_max_potential, 'w') as file:
                file.write(max_potential_value)
                print(max_potential_value)
            with sftp.file(file_path_start_potential, 'w') as file:
                file.write(start_potential_value)
            with sftp.file(file_path_step_potential, 'w') as file:
                file.write(step_potential_value)
            with sftp.file(file_path_time_interval, 'w') as file:
                file.write(time_interval_value)
            with sftp.file(file_path_total_cycle, 'w') as file:
                file.write(total_cycle_value)
            
            
        finally:
            sftp.close()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        ssh.close()
        print("SSH connection closed")
    
    threading.Thread(target=execute_code, args=(analysing,options_frame,plot_frame,raw_file_name)).start()

    

def execute_code(analysing,options_frame,plot_frame,raw_file_name):
    
    program_path = '/home/pi/dpv/experiment'  # Replace with the path to your program
    program_command = './bio_chemical_process_copy'  # Replace with the command to execute your program

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:

        ssh.connect(hostname, username=username, password=password)
        print("SSH connection established.")

        stdin, stdout, stderr = ssh.exec_command(f'cd {program_path}; sudo {program_command}')

        output = stdout.read().decode('utf-8')
        if output:
            print("Output:")
            print(output)

        error = stderr.read().decode('utf-8')
        if error:
            print("Error:")
            print(error)

    except paramiko.SSHException as e:
        print(f"SSH connection failed: {e}")

    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", "Failed")

    finally:
        ssh.close()
        print("SSH connection closed.")
    
    analysing.pack_forget()
    plot_button = Button(options_frame, text="Plot",bg="#3572b9", fg="white",font=('Helvetica', 12), command=lambda:on_plot_button_click(plot_frame,raw_file_name,options_frame))
    plot_button.pack(pady=5)

def submit_entries(entry1, entry2, entry3):
    global hostname,username,password
    hostname = entry1.get()
    username = entry2.get()
    password = entry3.get()
    print("Hostname:", hostname)
    print("Username:", username)
    print("Password:", password)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname, port, username, password)
        print("Connected succesfully")
        
    except Exception as e:
        print("Unable to connect")
        messagebox.showerror("Error", "Unable to connect")
        sys.exit(1)

    finally:
        ssh.close()
        print("SSH connection closed")
        new_file(root)

def create_labeled_image_login(parent, photo1,photo2,photo3):
    frame = Frame(parent,bg="white")
    label1 = Label(frame, image=photo1,bg="white")
    label2 = Label(frame, image=photo2,bg="white")
    label3 = Label(frame, image=photo3,bg="white")
    label1.pack(side='left', padx=(0, 0))
    label2.pack(side='left', padx=(0, 0))
    label3.pack(side='left', padx=(0, 0))
    frame.pack(pady=0)

def login_page(root):
    
    for widget in root.winfo_children():
        widget.destroy()
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    video_path ="Images\\Video_bg2.mp4" # Replace with your video path
    vid = cv2.VideoCapture(video_path)

    video_label = Label(root)
    video_label.place(relwidth=1, relheight=1) 

    update_video(video_label, vid)

    right_frame = Frame(root, width=200, bg='white')
    right_frame.grid(row=0, column=1,sticky='w') 
    image1 = Image.open("Images\\cdac_logo.png")  # Replace with your image path
    image2 = Image.open("Images\\institute_logo.png")  # Replace with your image path
    image3 = Image.open("Images\\logo.png")
    image4 = Image.open("Images\\meity_logo.png")
            
    image1 = image1.resize((120, 75), Image.LANCZOS)
    image2 = image2.resize((120, 75), Image.LANCZOS)
    image3 = image3.resize((120, 75), Image.LANCZOS)
    image4 = image4.resize((300, 150), Image.LANCZOS)
          
    photo1 = ImageTk.PhotoImage(image1)
    photo2 = ImageTk.PhotoImage(image2)
    photo3 = ImageTk.PhotoImage(image3)
    photo4 = ImageTk.PhotoImage(image4)

    create_labeled_image_login(right_frame,photo1,photo2,photo3)
    Label(right_frame,text="Sign in CG-STAT",bg="white",font=('Helvetica', 18, 'bold')).pack(pady=20)
    Label(right_frame, text="IP Address:",bg="white",font=('Helvetica', 12)).pack(pady=10)
    entry1 = Entry(right_frame,font=('Helvetica', 12))
    entry1.pack(pady=5)
    Label(right_frame, text="Username:",bg="white",font=('Helvetica', 12)).pack(pady=10)
    entry2 = Entry(right_frame,font=('Helvetica', 12))
    entry2.pack(pady=5)
    Label(right_frame, text="Password:",bg="white",font=('Helvetica', 12)).pack(pady=10)
    entry3 = Entry(right_frame,font=('Helvetica', 12))
    entry3.pack(pady=5)
    submit_button = Button(right_frame,bg="#3572b9" ,fg="white",text="Submit",font=('Helvetica', 12), command=lambda: submit_entries(entry1, entry2, entry3))
    submit_button.pack(pady=20)
    label = Label(right_frame, image=photo4,bg="white")
    label.pack()
    root.photo1 = photo1
    root.photo2 = photo2
    root.photo3 = photo3
    root.photo4 = photo4



def home_screen(root):
    video_path ="Images\\Video_bg4.mp4" # Replace with your video path
 
    cap = cv2.VideoCapture(video_path)

    def stream():
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, ((screen_width), (screen_height-60))) 
            frame_image = ImageTk.PhotoImage(Image.fromarray(frame))
            video_label.config(image=frame_image)
            video_label.image = frame_image
        
        cap.release()
        login_page(root)

    video_label = Label(root)
    video_label.pack()

    threading.Thread(target=stream).start()
    


root=Tk()
root.title("CG-STAT")
root.iconbitmap(r"Images\\cgstat_icon.ico")
center_window(root,800,500)
home_screen(root)
root.mainloop()


