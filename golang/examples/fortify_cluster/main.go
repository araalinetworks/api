package main

import (
	"flag"
	"fmt"
	"os"

	"github.com/araalinetworks/api/golang/araalictl"
)

func main() {

	var tenantID, clusterName string
	flag.StringVar(&tenantID, "id", "", "specify tenant")
	flag.StringVar(&clusterName, "cluster-name", "", "specify user name")

	flag.Parse()

	if tenantID == "" {
		fmt.Println("-id must be specified")
		os.Exit(1)
	}
	araalictl.FortifyK8sCluster(tenantID, clusterName)
}
