package main

import (
	"flag"
	"fmt"
	"os"

	"../../araalictl"
)

func main() {

	var op, tenantID, tenantName, userEmail, userName string
	flag.StringVar(&op, "op", "ADD", "specify op(ADD/DEL/ADD-USER/DEL-USER)")
	flag.StringVar(&tenantID, "id", "", "specify tenant")
	flag.StringVar(&tenantName, "name", "", "specify tenant name")
	flag.StringVar(&userEmail, "user-email", "", "specify user email")
	flag.StringVar(&userName, "user-name", "", "specify user name")

	flag.Parse()

	if op == "ADD" {
		if userEmail == "" || userName == "" {
			fmt.Println("-user-email and -user-name must be specified when op=ADD")
			os.Exit(1)
		}
		araalictl.TenantCreate(userEmail, tenantName, userName)
	} else if op == "DEL" {
		if tenantID == "" {
			fmt.Println("-id must be specified when op=DEL")
			os.Exit(1)
		}
		araalictl.TenantDelete(tenantID)
	} else if op == "ADD-USER" {
		if tenantID == "" || userEmail == "" || userName == "" {
			fmt.Println("-id, -user-email and -user-name must be specified when op=ADD-USER")
			os.Exit(1)
		}
		araalictl.TenantAddUser(tenantID, userEmail, userName)
	} else if op == "DEL-USER" {
		if tenantID == "" || userEmail == "" || userName == "" {
			fmt.Println("-id, -user-email and -user-name must be specified when op=DEL-USER")
			os.Exit(1)
		}
		araalictl.TenantDeleteUser(tenantID, userEmail, userName)
	}
}
