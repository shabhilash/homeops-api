import os


# TODO : Add service validation to check if the service is running

def service_action(name, action="status"):
    """
    Function to perform requested actions on service \n
    @param name: svc \n
    @param action: action \n
    @return: bool \n
    """
    if os.system(f"sudo systemctl {action} {name}"):
        return True
    else:
        return False