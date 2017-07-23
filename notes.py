# AVOID WRITING FILE TO DISK
# It is possible to get prices from the API without writing a file to disk.
# Uses the urlopen method of urllib.request
# This approach is used for get_total_mkt()

def get_data_nofile(targeturl):
    import urllib.request
    import json
    
    with urllib.request.urlopen(targeturl) as response:
        raw_data = response.read()

    # that gives a bytes array, which needs to be converted to a string 
    # before using json.loads on it

    string = raw_data.decode("utf-8")
    data = json.loads(string)
    
    return data


# ADD COLORS

def print_color():
    print("\x1b[1;31;40m" + "This is colored" +  "\x1b[0m")


# ADD GUI
# RECORD HISTORY
