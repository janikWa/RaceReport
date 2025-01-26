import os
import shutil
import subprocess

def create_report(path, name):
    #create new folder if not exist
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True) 
    
    #output path 
    output_file = f"RaceReport_{name}.html"
    
    # specify command 
    command = [
        "quarto", 
        "render", 
        "report.qmd", 
        f"-P", f"name={name}", 
        f"-P", f"source={path}", 
        "--output", output_file 
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Report successfully created at: {os.path.join(os.getcwd(), output_file)}")

        # Move the generated HTML to the reports folder
        shutil.move(output_file, os.path.join(output_dir, output_file))
        print(f"Report moved to: {os.path.join(output_dir, output_file)}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")

# Example usage
create_report("https://my.raceresult.com/309137/#3_EFFC53", "Winterlaufserie Rheinzabern - 15km")
