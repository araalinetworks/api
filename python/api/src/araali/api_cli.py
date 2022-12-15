import argparse

from . import api
from . import utils

if __name__ == "__main__":                                                      
    parser = argparse.ArgumentParser(description = 'utils')                     
    parser.add_argument("-w", "--what", help="command to run")
    parser.add_argument("-t", "--tenant", help="tenant")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose")
    parser.add_argument("-o", "--op", choices=["DEL", "ADD"], help="verbose")
    parser.add_argument("-q", "--quiet", action="store_true", help="count by unique values")
    parser.add_argument("-c", "--countby", help="count by unique values")       
    parser.add_argument("-g", "--groupby", help="groub by (key)")               
    parser.add_argument("-f", "--filterby", help="filter by (key)")             
    args = parser.parse_args() 

    if args.verbose: api.g_debug = True
    api = api.API()

    if args.what == "deltenant":
        print(api.delete_tenant(tenant=args.tenant))
    if args.what == "enforced":
        assert args.tenant, "need to specify tenant"
        if input("are you sure?> ") == "yes":
            assert args.op, "need to specify op"
            api.set_enforced(op=args.op, zone="poczone", app="kube-system", pod="araali-fw", container="araali-fw",
                tenant=args.tenant)

        utils.dump_table(api.get_enforced(args.tenant)[0], quiet=args.quiet,
                filterby=args.filterby, countby=args.countby, groupby=args.groupby)
