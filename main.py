import os
import shutil
import datetime
import paramiko
import time
import subprocess
import sys
# import numpy



def command_parallel_run_by_SSH(remote_folder,local_folder):
    hostname = 'newgate3.phys.huji.ac.il'
    username = 'elie'
    password = 'groogroo0'
    port = 22345
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port=port, username=username, password=password)
    sftp = ssh.open_sftp()

    try:
        shell = ssh.invoke_shell()
        print('------------------------------------\n')
        shell.send(f"cd {remote_folder}\n")
        time.sleep(10)
        output = shell.recv(65535).decode('utf-8')
        print(output)
        print('------------------------------------\n')
        shell.send("ls\n")
        time.sleep(10)
        output = shell.recv(65535).decode('utf-8')
        print(output)
        print('------------------------------------\n')
        shell.send("sbatch parallel_run\n")
        time.sleep(10)
        output = shell.recv(65535).decode('utf-8')
        print(output)
        print('------------------------------------\n')
        shell.send("squeue\n")
        time.sleep(10)
        output = shell.recv(65535).decode('utf-8')
        output_list = output.strip().split("\n")
        print(output)

        while True:

            if len(output_list) == 3:
                  break
            else:
                shell.send("squeue\n")
                time.sleep(10)
                output = shell.recv(65535).decode('utf-8')
                output_list = output.strip().split("\n")
        remote_file_list = sftp.listdir(remote_folder)


        for remote_file_name in remote_file_list:
            if remote_file_name != "atoms.fcc.edge.pad" and remote_file_name != "dimensions.ini" and remote_file_name != "dislocations.ini" and remote_file_name != "log.lammps" and remote_file_name != "main.in" and remote_file_name != "parallel_run" :
                remote_file_path = remote_folder + '/' + remote_file_name
                local_file_path = local_folder + '/' + remote_file_name
                sftp.get(remote_file_path, local_file_path)
        print(output)
        print("in the try \n")
    except Exception as e:
        print("in the except \n")
        print(f"Error occurred: {str(e)}")
    ssh.close()
    sftp.close()
# elie R

def copy_folder_by_SSH(local_folder, run_list):
    remote_folder = '/home/elie/git_projects/dislocation_velocity/ali'
    remote_path = ""
    # Define the SSH connection parameters
    hostname = 'newgate3.phys.huji.ac.il'
    username = 'elie'
    password = 'groogroo0'
    port = 22345

    # Create an SSH client and connect to the remote host
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port=port, username=username, password=password)

    # Create an SFTP client and transfer the files
    sftp = ssh.open_sftp()
    for root, dirs, files in os.walk(local_folder):
        for dir in dirs:
            if "run" in dir and dir not in run_list:
                run_list.append(dir)
                try:
                    remote_path = remote_folder + '/' + dir
                    sftp.mkdir(remote_path)
                    for root2, dirs2, files2 in os.walk(local_folder + '\\' + dir):

                        for file in files2:
                            try:
                                local_path2 = os.path.join(root2, file)
                                remote_path2 = remote_folder + '/' + dir + '/' + file
                                sftp.put(local_path2, remote_path2)
                            except Exception as e:
                                print(f"Error creating file: {str(e)}")

                        # new_remote_folder = remote_path.replace("/home/elie/", "")
                        # --------------------------------------------------------------------
                        # local_folder2=local_folder + '\\' + dir
                        # command_parallel_run_by_SSH(new_remote_folder,shell,local_folder2,sftp)
                        # check = True

                        # ---------------------------------------------------------------------
                except Exception as e:
                    print(f"Error creating directory: {str(e)}")

        break


    sftp.close()
    ssh.close()
    return remote_path


def name_creating(pressure):
    name = "run_"
    current_time = datetime.datetime.now()
    current_date = datetime.date.today()
    name += (current_date.strftime("%Y%m%d"))[2:] + "_"
    name += current_time.strftime("%H") + "_pressure_" + str(pressure)
    return name


def create_folder(name, pressure):
    line_to_change = "fix 1 all npt temp 300 300 0.05 aniso 0 0 0.17 xy 0 0 0.17 couple none drag 0.1\n"
    line_with_pressure = "fix 1 all npt temp 300 300 0.05 aniso 0 0 0.17 xy 0 " + str(pressure) + " 0.17 couple none drag 0.1\n"

    if not os.path.exists(name):
        os.mkdir(name)
        current_dir = os.getcwd()
        # Set the paths for the source and destination folders
        src_folder = os.path.join(current_dir, "source_folder")
        dst_folder = os.path.join(current_dir, name)
        if os.path.exists(dst_folder):
            shutil.rmtree(dst_folder)

        shutil.copytree(src_folder, dst_folder)
        # open main.in and change the pressure
        # Set the path to the file
        filepath = dst_folder + "\main.in"

        # Open the file and read its contents
        with open(filepath, "r") as file:
            lines = file.readlines()

        # Modify the desired line
        # print(lines[26])
        for x in range(len(lines)):
            if lines[x] == line_to_change:
                lines[x] = line_with_pressure
        # Write the modified contents back to the file
        with open(filepath, "w") as file:
            file.writelines(lines)
        return current_dir
    else:
        return os.getcwd()

def write_dislocations_and_dimensions():
    # Open file in write mode
    try:
        dimensions_file = open("fcc_learning/dimensions.ini", "w+")
        dislocations_file = open("fcc_learning/dislocations.ini", "w+")
        # Get input from user
        new_contents = dimensions_file.read()
        new_contents2 = dislocations_file.read()
        print("enter the dimensions:\n")
        nx_input = input("Enter nx: ")
        ny_input = input("Enter ny: ")
        nz_input = input("Enter nz: ")

        dimensions_write="nx="+nx_input+"\n"+"ny="+ny_input+"\n"+"nz="+nz_input
        dimensions_file.write(dimensions_write)
        dislocations_write = ""
        lines=input("How many dislocations: ")
        i=0
        while i < int(lines):
            location=input("Enter location: ")
            dislocation=input("Enter dislocation: ")
            burgers=input("Enter burgers victor : ")
            if i ==int(lines)-1:
                dislocations_write+=location+" "+dislocation+" "+burgers
            else:
                dislocations_write += location + " " + dislocation + " " + burgers+"\n"
            i+=1
        dislocations_file.write(dislocations_write)
    except IOError:
        print("Could not open file")
    # Write input to file
    # file.write(user_input)

    # Close the file
    # file.close()
def execute_fcc_dislocations_on_fcc_learning():
    # Path to the Python executable
    # python_path = 'python'
    #
    # # Path to the script to be executed
    # script_path = 'fcc_dislocations.py'
    #
    # # Command line arguments to be passed to the script
    # args = ['fcc_learning']
    #
    # # Construct the command to be executed
    # cmd = [python_path, script_path] + args
    #
    # # Use subprocess.run to execute the command
    # result = subprocess.run(cmd, capture_output=True)

    # Print the result of the command
    # print(result)
    foldername = "foldername"

    # Replace "filename.py" with the name of your Python file.
    filename = "filename.py"

    # Run the Python file.
    subprocess.run(["python", "fcc_dislocations.py", "fcc_learning"])

    # subprocess.run(['python', 'fcc_dislocations.py', 'fcc_learning'])
def copy_from_fcc_learning_to_source_folder():
    current_dir = os.getcwd()
    current_dir = os.getcwd()
    files = os.listdir(current_dir)
    # Print the current working directory
    print(current_dir)
    source_dislocations = current_dir+'\\fcc_learning\\dislocations.ini'
    destination_dislocations = current_dir+'\\source_folder\\dislocations.ini'
    # # current_dir = os.getcwd()
    # files = os.listdir(source_dislocations)
    source_dimensions = current_dir+'\\fcc_learning\\dimensions.ini'
    destination_dimensions = current_dir+'\\source_folder\\dimensions.ini'
    source_file = current_dir+'\\fcc_learning\\atoms_with_dislocations'
    destination_file = current_dir+'\\source_folder\\atoms.fcc.edge.pad'

    # Copy the file
    shutil.copy(source_dislocations, destination_dislocations)
    shutil.copy(source_dimensions, destination_dimensions)
    shutil.copy(source_file, destination_file)
if __name__ == '__main__':
    write_dislocations_and_dimensions()
    # # print(numpy.__version__)
    # print(",,,,")
    execute_fcc_dislocations_on_fcc_learning()
    copy_from_fcc_learning_to_source_folder()

    pressure = 0
    run_list=[]
    increasment = 500
    folder_name = "run_"
    max_pressure = 3000
    while pressure <= max_pressure:
        folder_name = name_creating(pressure)
        local_folder = create_folder(folder_name, pressure)
        local_folder2 = local_folder + '\\' + folder_name
        remote_folder =copy_folder_by_SSH(local_folder,run_list)
        new_remote_folder = remote_folder.replace("/home/elie/", "")
        command_parallel_run_by_SSH(new_remote_folder,local_folder2)
        pressure += increasment
        print(folder_name)
    pressure = 0
    max_pressure = 3000
