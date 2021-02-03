package main

import (
	"flag"
	"fmt"
	"os"

	"../../araalictl"
)

func main() {

	var op, tenantID, tenantName, userEmail, userName string
	flag.StringVar(&op, "op", "ADD", "specify op(ADD/DEL)")
	flag.StringVar(&tenantID, "id", "", "specify tenant")
	flag.StringVar(&tenantName, "name", "", "specify tenant name")
	flag.StringVar(&userEmail, "user-email", "", "specify user email")
	flag.StringVar(&userName, "user-name", "", "specify user name")

	flag.Parse()

	if op == "ADD" {
		if tenantID == "" || userEmail == "" || userName == "" {
			fmt.Println("-id, -user-email and -user-name must be specified when op=ADD")
			os.Exit(1)
		}
		araalictl.TenantCreate(tenantID, userEmail, tenantName, userName)
	} else {
		if tenantID == "" {
			fmt.Println("-id must be specified when op=DEL")
			os.Exit(1)
		}
		araalictl.TenantDelete(tenantID)
	}
}
