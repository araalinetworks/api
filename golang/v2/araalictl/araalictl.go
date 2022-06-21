package araalictl

import (
	"context"
	"encoding/hex"
	"fmt"
	"net"
	"time"

	"araali.proto/araali_api_service"

	"google.golang.org/grpc"
	"google.golang.org/grpc/metadata"
	"google.golang.org/protobuf/types/known/timestamppb"
)

const ApiDialTimeout = 30

var backend = "nightly.aws.araalinetworks.com"
var token = ""

func SetBackend(b string) {
	backend = b
}

func SetToken(t string) {
	token = t
}

func getAPIURL() (string, error) {
	url := fmt.Sprintf("api-%s", backend)
	ips, err := net.LookupIP(url)
	if false {
		fmt.Println(ips, err)
	}
	if err == nil {
		return url + ":443", nil
	}
	return "", err
}

// TODO: Cache and re-use if possible
func getApiClient() (context.Context, context.CancelFunc, araali_api_service.AraaliAPIClient) {
	var err error

	// Get the API FQDN:port
	url, err := getAPIURL()
	if err != nil {
		fmt.Println(fmt.Sprintf("Could not get API FQDN. Err: %v", url, token, err))
		return nil, nil, nil
	}

	checkConnection := func(url string) error {
		conn, err := net.DialTimeout("tcp", url, time.Duration(ApiDialTimeout)*time.Second)
		if err == nil {
			conn.Close()
		}
		return err
	}

	for i := 0; i < 3; i++ {
		if err = checkConnection(url); err == nil {
			break
		}
	}
	if err != nil {
		fmt.Println(fmt.Sprintf("Could not connect to %v (Token: %v). Err: %v",
			url, token, err))
		return nil, nil, nil
	}

	// Get the gRPC handle
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Minute)
	conn, err := grpc.DialContext(ctx, url, grpc.WithInsecure())
	if err != nil {
		fmt.Println(fmt.Sprintf("Could not connect to %v (Token: %v). Err: %v",
			url, token, err))
		return nil, nil, nil
	}

	// Set access token for authorization

	md := metadata.New(map[string]string{"authorization": fmt.Sprintf("Bearer %s", token)})
	ctx = metadata.NewOutgoingContext(ctx, md)

	// Get API client handle
	araaliUIConnection := araali_api_service.NewAraaliAPIClient(conn)
	newCtx, cancel := context.WithTimeout(ctx, 10*time.Minute)
	clientDeadline := time.Now().Add(time.Duration(10) * time.Minute)
	newCtx, _ = context.WithDeadline(newCtx, clientDeadline)
	return newCtx, cancel, araaliUIConnection
}

//
// Tenant and User Update Operations
//

// TenantCreate - returns tenant-id
func TenantCreate(name, adminName, adminEmail string, freemium bool) (*araali_api_service.CreateTenantResponse, error) {
	if len(adminEmail) == 0 {
		return nil, fmt.Errorf("invalid adminEmail (%v)", adminEmail)
	}

	ctx, cancel, api := getApiClient()
	if api == nil {
		return nil, fmt.Errorf("could not get API handle")
	}
	defer cancel()

	req := &araali_api_service.TenantRequest{
		Tenant: &araali_api_service.Tenant{
			AdminEmail: adminEmail,
		},
		Op: araali_api_service.TenantRequest_ADD,
	}
	resp, err := api.CreateTenant(ctx, req)
	if err != nil {
		return nil, err
	}
	return resp, nil
}

// TenantDelete
func TenantDelete(tenantID string) (*araali_api_service.AraaliAPIResponse, error) {
	if len(tenantID) == 0 {
		return nil, fmt.Errorf("invalid tenantid (%v)", tenantID)
	}

	ctx, cancel, api := getApiClient()
	if api == nil {
		return nil, fmt.Errorf("could not get API handle")
	}
	defer cancel()

	req := &araali_api_service.TenantRequest{
		Tenant: &araali_api_service.Tenant{
			Id: tenantID,
		},
		Op: araali_api_service.TenantRequest_DEL,
	}
	resp, err := api.DeleteTenant(ctx, req)
	if err != nil {
		return nil, err
	}
	return resp, nil
}

// UserAdd
func UserAdd(tenantID, userName, userEmail, role string) (*araali_api_service.AraaliAPIResponse, error) {
	if len(tenantID) == 0 {
		return nil, fmt.Errorf("invalid tenantid (%v)", tenantID)
	} else if len(userEmail) == 0 {
		return nil, fmt.Errorf("invalid user email (%v)", userEmail)
	}

	ctx, cancel, api := getApiClient()
	if api == nil {
		return nil, fmt.Errorf("could not get API handle")
	}
	defer cancel()

	r := araali_api_service.AraaliUser_USER
	if role == "ADMIN" {
		r = araali_api_service.AraaliUser_ADMIN
	}
	req := &araali_api_service.UserRequest{
		Tenant: &araali_api_service.Tenant{
			Id: tenantID,
		},
		User: &araali_api_service.AraaliUser{
			Email: userEmail,
			Role:  r,
		},
		Op: araali_api_service.UserRequest_ADD,
	}
	resp, err := api.AddUser(ctx, req)
	if err != nil {
		return nil, err
	}
	return resp, nil
}

// UserDelete
func UserDelete(tenantID, userEmail string) (*araali_api_service.AraaliAPIResponse, error) {
	if len(tenantID) == 0 {
		return nil, fmt.Errorf("invalid tenantid (%v)", tenantID)
	} else if len(userEmail) == 0 {
		return nil, fmt.Errorf("invalid user email (%v)", userEmail)
	}

	ctx, cancel, api := getApiClient()
	if api == nil {
		return nil, fmt.Errorf("could not get API handle")
	}
	defer cancel()

	req := &araali_api_service.UserRequest{
		Tenant: &araali_api_service.Tenant{
			Id: tenantID,
		},
		User: &araali_api_service.AraaliUser{
			Email: userEmail,
		},
		Op: araali_api_service.UserRequest_DEL,
	}
	resp, err := api.DeleteUser(ctx, req)
	if err != nil {
		return nil, err
	}
	return resp, nil
}

// ListAssets
func ListAssets(tenantID, zone, app string, activeVm, inactiveVm, activeContainer, inactiveContainer bool,
	startTime, endTime time.Time) (*araali_api_service.ListAssetsResponse, int, int, error) {
	if len(tenantID) == 0 {
		return nil, -1, -1, fmt.Errorf("invalid tenantid (%v)", tenantID)
	}

	ctx, cancel, api := getApiClient()
	if api == nil {
		return nil, -1, -1, fmt.Errorf("could not get API handle")
	}
	defer cancel()

	assetFilter := &araali_api_service.AssetFilter{
		ListActiveVm:          activeVm,
		ListActiveContainer:   activeContainer,
		ListInactiveVm:        inactiveVm,
		ListInactiveContainer: inactiveContainer,
	}
	req := &araali_api_service.ListAssetsRequest{
		Tenant: &araali_api_service.Tenant{
			Id: tenantID,
		},
		Zone:   zone,
		App:    app,
		Filter: assetFilter,
		Time: &araali_api_service.TimeSlice{
			StartTime: timestamppb.New(startTime),
			EndTime:   timestamppb.New(endTime),
		},
	}
	resp, err := api.ListAssets(ctx, req)
	if err != nil {
		return nil, -1, -1, err
	}
	vmCount := 0
	containerCount := 0
	for _, asset := range resp.Assets {
		if asset.State == araali_api_service.AssetState_ACTIVE {
			if asset.Type == araali_api_service.AssetType_CONTAINER {
				containerCount++
			}
			if asset.Type == araali_api_service.AssetType_VIRTUAL_MACHINE {
				vmCount++
			}
		}
	}
	return resp, vmCount, containerCount, nil
}

type AlertPage struct {
	tenantID    string
	start       time.Time
	end         time.Time
	all         bool
	count       int32
	PagingToken []byte
	Alerts      []*araali_api_service.Link
}

func (alertPage *AlertPage) HasNext() bool {
	if string(alertPage.PagingToken) == "" {
		return false
	}
	return true
}

func (alertPage *AlertPage) NextPage() ([]*araali_api_service.Link, error) {
	listOfLinks := []*araali_api_service.Link{}
	if !alertPage.HasNext() {
		return listOfLinks, fmt.Errorf("Next page doesn't exist")
	}

	// Get Alerts with paging token
	ctx, cancel, api := getApiClient()
	if api == nil {
		return listOfLinks, fmt.Errorf("Could not get API handle")
	}
	defer cancel()

	alertFilter := &araali_api_service.AlertFilter{
		RollupType: araali_api_service.LinkState_BASELINE_ALERT,
		Time: &araali_api_service.TimeSlice{
			StartTime: timestamppb.New(alertPage.start),
			EndTime:   timestamppb.New(alertPage.end),
		},
		ListAllAlerts: alertPage.all,
	}

	req := &araali_api_service.ListAlertsRequest{
		Tenant: &araali_api_service.Tenant{
			Id: alertPage.tenantID,
		},
		Count:       alertPage.count,
		PagingToken: string(alertPage.PagingToken),
		Filter:      alertFilter,
	}
	resp, err := api.ListAlerts(ctx, req)
	if err != nil {
		return listOfLinks, err
	}

	fmt.Printf("ListAlerts GetNext Response: %v", resp)

	if resp.Response.Code != araali_api_service.AraaliAPIResponse_SUCCESS {
		return listOfLinks, fmt.Errorf("ListAlerts API failed")
	}

	if err != nil || len(resp.Links) == 0 {
		alertPage.PagingToken = []byte{}
		return listOfLinks, err
	}

	listOfLinks = resp.Links
	token, err := hex.DecodeString(listOfLinks[len(listOfLinks)-1].PagingToken)
	if err != nil {
		return listOfLinks, fmt.Errorf("Error decoding token")
	}

	alertPage.PagingToken = token
	alertPage.Alerts = listOfLinks
	return listOfLinks, nil
}

func ListAlerts(tenantID string, startTime, endTime time.Time,
	count int32, all bool, pagingToken string) (AlertPage, error) {
	alertPage := AlertPage{
		tenantID: tenantID,
		start:    startTime,
		end:      endTime,
		all:      all,
		count:    count,
	}
	if len(tenantID) == 0 {
		return alertPage, fmt.Errorf("invalid tenantid (%v)", tenantID)
	}
	if len(pagingToken) != 0 {
		token, err := hex.DecodeString(pagingToken)
		if err == nil {
			alertPage.PagingToken = token
		}
	}

	ctx, cancel, api := getApiClient()
	if api == nil {
		return alertPage, fmt.Errorf("could not get API handle")
	}
	defer cancel()

	alertFilter := &araali_api_service.AlertFilter{
		RollupType: araali_api_service.LinkState_BASELINE_ALERT,
		Time: &araali_api_service.TimeSlice{
			StartTime: timestamppb.New(alertPage.start),
			EndTime:   timestamppb.New(alertPage.end),
		},
		ListAllAlerts: alertPage.all,
	}

	req := &araali_api_service.ListAlertsRequest{
		Tenant: &araali_api_service.Tenant{
			Id: alertPage.tenantID,
		},
		Count:       alertPage.count,
		PagingToken: string(alertPage.PagingToken),
		Filter:      alertFilter,
	}
	resp, err := api.ListAlerts(ctx, req)
	if err != nil {
		return alertPage, err
	}

	if resp.Response.Code != araali_api_service.AraaliAPIResponse_SUCCESS {
		return alertPage, fmt.Errorf("ListAlerts API failed")
	}

	fmt.Printf("ListAlerts Response: %v", resp)

	alertPage.Alerts = resp.Links
	token, err := hex.DecodeString(alertPage.Alerts[len(alertPage.Alerts)-1].PagingToken)
	if err != nil {
		return alertPage, fmt.Errorf("error decoding token")
	}
	alertPage.PagingToken = token

	return alertPage, nil
}

// GetAlertCard

func GetAlertCard(tenantID string, startTime, endTime time.Time) (*araali_api_service.GetAlertCardResponse, error) {
	if len(tenantID) == 0 {
		return nil, fmt.Errorf("invalid tenantid (%v)", tenantID)
	}
	ctx, cancel, api := getApiClient()
	if api == nil {
		return nil, fmt.Errorf("could not get API handle")
	}
	defer cancel()

	req := &araali_api_service.GetAlertCardRequest{
		Tenant: &araali_api_service.Tenant{
			Id: tenantID,
		},
		Time: &araali_api_service.TimeSlice{
			StartTime: timestamppb.New(startTime),
			EndTime:   timestamppb.New(endTime),
		},
	}
	resp, err := api.GetAlertCard(ctx, req)
	if err != nil {
		return nil, err
	}
	return resp, nil
}

// ListZones
func ListZones(tenantID, zone, app string, startTime, endTime time.Time, fetchLinks bool) (*araali_api_service.ListZonesResponse, error) {
	if len(tenantID) == 0 {
		return nil, fmt.Errorf("invalid tenantid (%v)", tenantID)
	}

	ctx, cancel, api := getApiClient()
	if api == nil {
		return nil, fmt.Errorf("could not get API handle")
	}
	defer cancel()

	req := &araali_api_service.ListZonesRequest{
		Tenant: &araali_api_service.Tenant{
			Id: tenantID,
		},
		Zone:       zone,
		App:        app,
		FetchLinks: fetchLinks,
		Time: &araali_api_service.TimeSlice{
			StartTime: timestamppb.New(startTime),
			EndTime:   timestamppb.New(endTime),
		},
	}
	resp, err := api.ListZones(ctx, req)
	if err != nil {
		return nil, err
	}
	return resp, nil
}

// ListLinks
func ListLinks(tenantID, zone, app, service string, startTime, endTime time.Time) (*araali_api_service.ListLinksResponse, error) {
	if len(tenantID) == 0 {
		return nil, fmt.Errorf("invalid tenantid (%v)", tenantID)
	}
	ctx, cancel, api := getApiClient()
	if api == nil {
		return nil, fmt.Errorf("could not get API handle")
	}
	defer cancel()

	req := &araali_api_service.ListLinksRequest{
		Tenant: &araali_api_service.Tenant{
			Id: tenantID,
		},
		Zone:    zone,
		App:     app,
		Service: service,
		Time: &araali_api_service.TimeSlice{
			StartTime: timestamppb.New(startTime),
			EndTime:   timestamppb.New(endTime),
		},
	}
	resp, err := api.ListLinks(ctx, req)
	if err != nil {
		return nil, err
	}
	return resp, nil
}

// ListInsights
func ListInsights(tenantID, zone string) (*araali_api_service.ListInsightsResponse, error) {
	if len(tenantID) == 0 {
		return nil, fmt.Errorf("invalid tenantid (%v)", tenantID)
	}
	ctx, cancel, api := getApiClient()
	if api == nil {
		return nil, fmt.Errorf("could not get API handle")
	}
	defer cancel()

	req := &araali_api_service.ListInsightsRequest{
		Tenant: &araali_api_service.Tenant{
			Id: tenantID,
		},
		Zone: zone,
	}
	resp, err := api.ListInsights(ctx, req)
	if err != nil {
		return nil, err
	}
	return resp, nil
}
