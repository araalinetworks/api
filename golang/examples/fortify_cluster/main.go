package main

import (
	"flag"
	"fmt"
	"os"

	yaml "gopkg.in/yaml.v2"

	"github.com/araalinetworks/api/golang/v1/araalictl"
)

func main() {

	var tenantID, clusterName, actlPath string
	var genHelm bool
	flag.StringVar(&actlPath, "actlPath", "", "araalictl path")
	flag.StringVar(&tenantID, "id", "", "specify tenant")
	flag.StringVar(&clusterName, "cluster-name", "", "specify user name")
	flag.BoolVar(&genHelm, "gen", false, "generate helm")

	flag.Parse()

	if len(actlPath) != 0 {
		araalictl.SetAraalictlPath(actlPath)
	}

	if tenantID == "" {
		fmt.Println("-id must be specified")
		os.Exit(1)
	}
	if genHelm {
		out, err := araalictl.FortifyK8SGenerateHelm(tenantID, clusterName)
		if err != nil {
			fmt.Println(err)
			return
		}
		outB, _ := yaml.Marshal(out)
		fmt.Println("\n## values.yaml ##")
		fmt.Printf("%v\n", string(outB))
	} else {
		out, err := araalictl.FortifyK8sCluster(tenantID, clusterName, true)
		if err != nil {
			fmt.Printf("Fortiy-K8s failed (%v)\n", err)
			return
		}
		fmt.Println(out)
	}
}
