package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"time"

	"./araalictl"
)

func main() {
	for {
		fmt.Printf("\nEnter command to run:\n")
		fmt.Printf("\t0: quit\n")
		fmt.Printf("\t1: zones_apps\n")
		fmt.Printf("\t2: zones_apps_links\n")
		fmt.Printf("\t3: summary\n")
		fmt.Printf("\t4: alert_card\n")
		fmt.Printf("\t5: alerts\n")

		reader := bufio.NewReader(os.Stdin)
		text, err := reader.ReadString('\n')
		if err != nil {
			return
		}
		text = strings.TrimSpace(text)

		if text == "0" {
			return
		}

		if text == "1" {
			for _, zone := range araalictl.GetZones(false, "") {
				fmt.Printf("%s:\n", zone.ZoneName)
				for _, app := range zone.Apps {
					fmt.Printf("\t%s\n", app.AppName)
				}
				fmt.Println()
			}
			continue
		}

		if text == "2" {
			for _, zone := range araalictl.GetZones(true, "") {
				fmt.Printf("%s:\n", zone.ZoneName)
				for _, app := range zone.Apps {
					fmt.Printf("\t%s\n", app.AppName)
					for _, link := range app.Links {
						fmt.Printf("\t\t%+v\n", link)
					}
				}
				fmt.Println()
			}
			continue
		}

		if text == "3" {
			summary := make(map[string]int)
			for _, zone := range araalictl.GetZones(true, "") {
				for _, app := range zone.Apps {
					for _, link := range app.Links {
						summary["type."+link.Type] += 1
						summary["state."+link.State] += 1
					}
				}
			}
			fmt.Printf("\nSummary:\n")
			for k, v := range summary {
				fmt.Printf("\t%-30s %d\n", k, v)
			}
			continue
		}

		if text == "4" {
			alertCard := araalictl.GetAlertCard("")
			fmt.Printf("%v\n", alertCard)
		}

		if text == "5" {
			startTime := time.Now().Add(-(3 * araalictl.ONE_DAY)).Unix()
			alertPage := araalictl.GetAlerts("", startTime, 0, 25)
			fmt.Printf("Fetched %d alerts.\n", len(alertPage.Alerts))
			for {
				if !alertPage.HasNext() {
					fmt.Println("Done fetching!")
					break
				}
				alertPage.NextPage()
				fmt.Printf("Fetched %d alerts.\n", len(alertPage.Alerts))
			}
		}
	}

	// unreachable code, left for sample reasons
	fmt.Printf("%+v\n", araalictl.GetLinks("azure3", "istio-system", "amk"))
}
