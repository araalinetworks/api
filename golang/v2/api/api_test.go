package api

import (
	"fmt"
	"os"
	"testing"
	"time"

	"google.golang.org/protobuf/types/known/timestamppb"

	"golang/v2/araali_api_service"
)

func setup(t *testing.T) {
	SetBackend("nightly.aws.araalinetworks.com")
	SetToken(os.Getenv("ARAALI_API_TOKEN"))
}

var verbose1 = 0

// TestAlerts calls ListAlerts since the beginning of time,
// checking for consistency with last baseline
func TestAlerts(t *testing.T) {
	setup(t)

	tenantID := "meta-tap"
	filter := araali_api_service.AlertFilter{
		Time: &araali_api_service.TimeSlice{
			StartTime: timestamppb.New(time.Date(1980, time.November, 0, 0, 0, 0, 0, time.UTC)),
			EndTime:   timestamppb.New(time.Now()),
		},
		ListAllAlerts:        false,
		OpenAlerts:           true,
		ClosedAlerts:         false,
		PerimeterIngress:     true,
		PerimeterEgress:      true,
		HomeNonAraaliIngress: true,
		HomeNonAraaliEgress:  true,
		AraaliToAraali:       true,
	}
	resp, err := ListAlerts(tenantID, &filter, 10, "")
	if verbose1 > 0 {
		fmt.Printf("\nR: %+v/%v\n", len(resp.Alerts), err)
	}
	if len(resp.Alerts) != 10 {
		t.Fatalf("ListAlerts() = %v, want 10", len(resp.Alerts))
	}
}

//Testing ListAlerts with specific Zone passed. Return only those zone specific alerts
func TestAlertsFilterValidZone(t *testing.T) {
	setup(t)

	zone := "nightlycommon"
	tenantID := "meta-tap"
	filter := araali_api_service.AlertFilter{
		Time: &araali_api_service.TimeSlice{
			StartTime: timestamppb.New(time.Date(1980, time.November, 0, 0, 0, 0, 0, time.UTC)),
			EndTime:   timestamppb.New(time.Now()),
		},
		ListAllAlerts:        false,
		OpenAlerts:           true,
		ClosedAlerts:         false,
		PerimeterIngress:     true,
		PerimeterEgress:      true,
		HomeNonAraaliIngress: true,
		HomeNonAraaliEgress:  true,
		AraaliToAraali:       true,
		//Zone:                 zone,
	}
	resp, err := ListAlerts(tenantID, &filter, 10, "")
	totalAlerts := len(resp.Alerts)

	if verbose1 > 0 {
		fmt.Printf("\nR: %+v/%v\n", totalAlerts, err)
	}

	counter := 0
	for _, s := range resp.Alerts {
		_, araaliEndpoint := s.Client.Info.(*araali_api_service.EndPoint_Araali)
		if araaliEndpoint {
			if s.Client.GetAraali().Zone == zone {
				counter++
			}
		}
	}

	//Validate whether all the alerts are corresponding to passed zone value
	if counter != totalAlerts {
		t.Fatalf("%v count in the response = %v, want %v", zone, counter, totalAlerts)
	}

}

//Testing ListAlerts with specific Zone passed which returns ZERO count
func TestAlertsFilterInvalidZone(t *testing.T) {
	setup(t)

	//zone := "invalidzone"
	tenantID := "meta-tap"
	filter := araali_api_service.AlertFilter{
		Time: &araali_api_service.TimeSlice{
			StartTime: timestamppb.New(time.Date(1980, time.November, 0, 0, 0, 0, 0, time.UTC)),
			EndTime:   timestamppb.New(time.Now()),
		},
		ListAllAlerts:        false,
		OpenAlerts:           true,
		ClosedAlerts:         false,
		PerimeterIngress:     true,
		PerimeterEgress:      true,
		HomeNonAraaliIngress: true,
		HomeNonAraaliEgress:  true,
		AraaliToAraali:       true,
		//Zone:                 zone,
	}
	resp, err := ListAlerts(tenantID, &filter, 10, "")
	if verbose1 > 0 {
		fmt.Printf("\nR: %+v/%v\n", len(resp.Alerts), err)
	}
	if len(resp.Alerts) != 0 {
		t.Fatalf("ListAlerts() = %v, want 0", len(resp.Alerts))
	}
}
