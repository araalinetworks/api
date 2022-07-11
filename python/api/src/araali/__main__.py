"""Used to execute modeule from the command line
    Fetches alerts and prints the count
"""
import api
import sys

def main():
    print("Got %s alerts" % len(api.API().get_alerts()[0]))

if __name__ == "__main__":
    sys.exit(main())
