package main

import (
	"fmt"
)

func main() {
	fmt.Printf("%+v\n", GetZones(false, "amk"))
	fmt.Printf("%+v\n", GetLinks("azure3", "istio-system", "amk"))
}
