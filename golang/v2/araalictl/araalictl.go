package araalictl

import (
	"context"
	"fmt"
	"net"
	"time"

	"araali.proto/araali_api_service"

	"google.golang.org/grpc"
	"google.golang.org/grpc/metadata"
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
func TenantCreate(name, adminName, adminEmail string, freemium bool) (string, error) {
	if len(adminEmail) == 0 {
		return "", fmt.Errorf("invalid adminEmail (%v)", adminEmail)
	}

	_, _, api := getApiClient()
	if api == nil {
		return "", fmt.Errorf("Could not get API handle")
	}

	return "", nil
}

// TenantDelete
func TenantDelete(tenantID string) error {
	if len(tenantID) == 0 {
		return fmt.Errorf("invalid tenantid (%v)", tenantID)
	}

	_, _, api := getApiClient()
	if api == nil {
		return fmt.Errorf("Could not get API handle")
	}

	return nil
}

// UserAdd
func UserAdd(tenantID, userName, userEmail, role string) error {
	if len(tenantID) == 0 {
		return fmt.Errorf("invalid tenantid (%v)", tenantID)
	} else if len(userEmail) == 0 {
		return fmt.Errorf("invalid user email (%v)", userEmail)
	}

	_, _, api := getApiClient()
	if api == nil {
		return fmt.Errorf("Could not get API handle")
	}

	return nil
}

// UserDelete
func UserDelete(tenantID, userEmail string) error {
	if len(tenantID) == 0 {
		return fmt.Errorf("invalid tenantid (%v)", tenantID)
	} else if len(userEmail) == 0 {
		return fmt.Errorf("invalid user email (%v)", userEmail)
	}

	_, _, api := getApiClient()
	if api == nil {
		return fmt.Errorf("Could not get API handle")
	}

	return nil
}
