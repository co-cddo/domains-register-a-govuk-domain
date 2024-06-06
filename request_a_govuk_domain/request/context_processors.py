import os


def environment(request):
    """
    Send the ENVIRONMENT variable to all views in order to display the correct
    phase banner
    """
    return {"environment": os.getenv("ENVIRONMENT", "dev")}
