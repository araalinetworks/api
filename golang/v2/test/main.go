package main

import (
	"flag"
	"fmt"
	"os"
	"time"

	"araali.proto/araali_api_service"

	"google.golang.org/protobuf/types/known/timestamppb"

	api "github.com/araalinetworks/araali/third_party/api/golang/v2/api"
)

func main() {

	var op, tenantID, tenantName, userEmail, userName string
	flag.StringVar(&op, "op", "ADD", "specify op(ADD/DEL/ADD-USER/DEL-USER/LIST-ASSETS/LIST-ALERTS/LIST-LINKS/LIST-INSIGHTS)")
	flag.StringVar(&tenantID, "id", "", "specify tenant")
	flag.StringVar(&tenantName, "name", "", "specify tenant name")
	flag.StringVar(&userEmail, "user-email", "", "specify user email")
	flag.StringVar(&userName, "user-name", "", "specify user name")

	flag.Parse()

	api.SetBackend("nightly.aws.araalinetworks.com")
	api.SetToken("")

	if op == "ADD" {
		if userEmail == "" || userName == "" {
			fmt.Println("-user-email and -user-name must be specified when op=ADD")
			os.Exit(1)
		}
		resp, err := api.TenantCreate(tenantName, userName, userEmail, true)
		fmt.Printf("Resp: %v/%v\n", resp, err)
	} else if op == "DEL" {
		if tenantID == "" {
			fmt.Println("-id must be specified when op=DEL")
			os.Exit(1)
		}
		resp, err := api.TenantDelete(tenantID)
		fmt.Printf("Resp: %v/%v\n", resp, err)
	} else if op == "ADD-USER" {
		if tenantID == "" || userEmail == "" || userName == "" {
			fmt.Println("-id, -user-email and -user-name must be specified when op=ADD-USER")
			os.Exit(1)
		}
		resp, err := api.UserAdd(tenantID, userName, userEmail, "ADMIN")
		fmt.Printf("Resp: %v/%v\n", resp, err)
	} else if op == "DEL-USER" {
		if tenantID == "" || userEmail == "" || userName == "" {
			fmt.Println("-id, -user-email and -user-name must be specified when op=DEL-USER")
			os.Exit(1)
		}
		resp, err := api.UserDelete(tenantID, userEmail)
		fmt.Printf("Resp: %v/%v\n", resp, err)
	} else if op == "LIST-ASSETS" {
		if tenantID == "" {
			fmt.Println("-id must be specified when op=LIST-ASSETS")
			os.Exit(1)
		}
		resp, vmCount, contCnt, err := api.ListAssets(tenantID, "app-chg", "app-chg", true, false, true, false, time.Now().Add(time.Duration(-10)*time.Minute), time.Now())
		fmt.Printf("Resp: %v/%v (%v, %v)\n", resp, err, vmCount, contCnt)
	} else if op == "LIST-ALERTS" {
		if tenantID == "" {
			fmt.Println("-id must be specified when op=LIST-ASSETS")
			os.Exit(1)
		}
		filter := araali_api_service.AlertFilter{
			Time: &araali_api_service.TimeSlice{
				//StartTime: timestamppb.New(time.Now().Add(time.Duration(-10) * time.Minute)),
				StartTime: timestamppb.New(time.Date(1979, time.November, 0, 0, 0, 0, 0, time.UTC)),
				EndTime:   timestamppb.New(time.Now()),
			},
			ListAllAlerts: false,
			OpenAlerts:    true,
			ClosedAlerts:  false,
			PerimeterEgress: true,
			PerimeterIngress: true,
			HomeNonAraaliEgress: true,
			HomeNonAraaliIngress: true,
			AraaliToAraali: true,
		}
		resp, err := api.ListAlerts(tenantID, &filter, 100, "")
		fmt.Printf("Resp: %v/%v\n", resp, err)
	} else if op == "LIST-LINKS" {
		if tenantID == "" {
			fmt.Println("-id must be specified when op=LIST-LINKS")
			os.Exit(1)
		}
		resp, err := api.ListLinks(tenantID, "app-chg", "app-chg", "",
			time.Now().Add(time.Duration(-10)*time.Minute), time.Now())
		fmt.Printf("Resp: %v/%v\n", resp, err)
	} else if op == "LIST-INSIGHTS" {
		if tenantID == "" {
			fmt.Println("-id must be specified when op=LIST-ASSETS")
			os.Exit(1)
		}
		resp, err := api.ListInsights(tenantID, "app-chg")
		fmt.Printf("Resp: %v/%v\n", resp, err)
	}
}
