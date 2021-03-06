package araalictl

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"syscall"
	"time"

	"gopkg.in/yaml.v2"
)

// Constants
const ONE_DAY = 24 * 60 * time.Minute

// FileExists - check if file exists
func FileExists(filename string) bool {
	_, err := os.Stat(filename)
	if os.IsNotExist(err) {
		return false
	}
	return true
}

// CommandDebug - logs every command that is executed
var CommandDebug = false

// RunControlOut takes a command and runs it, control is for whether to exit, allows output to go to stdout
func RunControlOut(cmdArgs []string, user string, exitOnFailure bool, out *bytes.Buffer) error {
	if CommandDebug {
		fmt.Println(cmdArgs, user, exitOnFailure)
	}
	cmd := exec.Command(cmdArgs[0], cmdArgs[1:]...)
	cmd.Env = os.Environ()
	if len(user) != 0 {
		cmd.SysProcAttr = &syscall.SysProcAttr{}
		uids, _ := RunControl([]string{"id", "-u", user}, "", true)
		uid, _ := strconv.Atoi(strings.TrimSpace(uids))
		gids, _ := RunControl([]string{"id", "-g", user}, "", true)
		gid, _ := strconv.Atoi(strings.TrimSpace(gids))
		cmd.SysProcAttr.Credential = &syscall.Credential{Uid: uint32(uid), Gid: uint32(gid)}
	}

	if out != nil {
		cmd.Stdout = out
		//cmd.Stderr = out // comment to not capture stderr
	} else {
		cmd.Stdin = os.Stdin
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
	}

	if err := cmd.Run(); err != nil {
		if exitOnFailure {
			fmt.Fprintln(os.Stderr, strings.Join(cmdArgs, " ")+": "+fmt.Sprint(err)+": "+out.String())
			os.Exit(1)
		} else {
			return err
		}
	}
	return nil
}

// RunControl takes a command and runs it, control is for whether to exit
func RunControl(cmdArgs []string, user string, exitOnFailure bool) (string, error) {
	var out bytes.Buffer
	err := RunControlOut(cmdArgs, user, exitOnFailure, &out)
	if err == nil {
		return out.String(), nil
	}
	return "", err
}

// RunStrControl takes a command string and runs it, control is for whether to exit
func RunStrControl(cmdstr, user string, exitOnFailure bool) (string, error) {
	return RunControl([]string{"sh", "-c", cmdstr}, user, exitOnFailure)
}

// RunAs - Run cmdstr as user
func RunAs(cmdstr, user string) string {
	ret, _ := RunStrControl(cmdstr, user, true)
	return ret
}

// RunCmd - Run cmdstr and collect/return output
func RunCmd(cmdstr string) string {
	return RunAs(cmdstr, "")
}

type Zone struct {
	ZoneName string `yaml:"zone_name"`
	Apps     []App
}

type App struct {
	AppName       string       `yaml:"app_name"`
	Links         []Link       `yaml:"links,omitempty"`
	AlertCounts   AlertCount   `yaml:"alert,omitempty"`
	ServiceCounts ServiceCount `yaml:"service,omitempty"`
	ComputeCounts ComputeCount `yaml:"compute,omitempty"`
}

type AlertCount struct {
	TotalAlerts            uint64 `yaml:"total_alerts,omitempty"`
	IngressAlerts          uint64 `yaml:"ingress_alerts,omitempty"`
	PerimeterIngressAlerts uint64 `yaml:"perimeter_ingress_alerts,omitempty"`
	InternalAlerts         uint64 `yaml:"internal_alerts,omitempty"`
	EgressAlerts           uint64 `yaml:"egress_alerts,omitempty"`
	PerimeterEgressAlerts  uint64 `yaml:"perimeter_egress_alerts,omitempty"`
}

type ServiceCount struct {
	TotalServices            uint64 `yaml:"total_services,omitempty"`
	IngressServices          uint64 `yaml:"ingress_services,omitempty"`
	PerimeterIngressServices uint64 `yaml:"perimeter_ingress_services,omitempty"`
	InternalServices         uint64 `yaml:"internal_services,omitempty"`
	EgressServices           uint64 `yaml:"egress_services,omitempty"`
	PerimeterEgressServices  uint64 `yaml:"perimeter_egress_services,omitempty"`
}

type ComputeCount struct {
	VirtualMachines uint32 `yaml:"virtual_machines,omitempty"`
	Containers      uint32 `yaml:"containers,omitempty"`
}

type AlertCard struct {
	TotalAlerts  uint64 `yaml:"alert_summary"`
	AlertDetails []Zone `yaml:"alert_details,omitempty"`
}

// Endpoint Object
type EndPoint struct {
	Zone          string `yaml:"zone,omitempty"`
	App           string `yaml:"app,omitempty"`
	outerApp      string
	Process       string `yaml:"process,omitempty"`
	BinaryName    string `yaml:"binary_name,omitempty"`
	ParentProcess string `yaml:"parent_process,omitempty"`
	DnsPattern    string `yaml:"dns_pattern,omitempty"`
	Subnet        string `yaml:"subnet,omitempty"`
	NetMask       uint32 `yaml:"netmask,omitempty"`
	DstPort       uint32 `yaml:"dst_port,omitempty"`

	OrigZone          string `yaml:"orig_zone,omitempty"`
	OrigApp           string `yaml:"orig_app,omitempty"`
	OrigProcess       string `yaml:"orig_process,omitempty"`
	OrigBinaryName    string `yaml:"orig_binary_name,omitempty"`
	OrigParentProcess string `yaml:"orig_parent_process,omitempty"`
	OrigDnsPattern    string `yaml:"orig_dns_pattern,omitempty"`
	OrigSubnet        string `yaml:"orig_subnet,omitempty"`
	OrigNetMask       uint32 `yaml:"orig_netmask,omitempty"`
	OrigDstPort       uint32 `yaml:"orig_dst_port,omitempty"`
}

// Link Object
type Link struct {
	Client      EndPoint
	Server      EndPoint
	Type        string
	Speculative bool
	State       string
	Timestamp   uint64
	UniqueId    string    `yaml:"unique_id"`
	NewState    string    `yaml:"new_state,omitempty"`
	PagingToken string    `yaml:"paging_token,omitempty"`
	AlertInfo   AlertInfo `yaml:"alert_info,omitempty"`
}

// AlertInfo object
type AlertInfo struct {
	CommunicationAlertType string `yaml:"communication_alert_type,omitempty"`
	ProcessAlertType       string `yaml:"process_alert_type,omitempty"`
}

// TenantCreate - to create a tenant
func TenantCreate(tenantID, userEmail, tenantName, UserName string) {
	RunCmd(fmt.Sprintf("/opt/araali/bin/araalictl tenant -op=add -id=%s -name=\"%s\" -user-email=%s -user-name=\"%s\"",
		tenantID, tenantName, userEmail, UserName))
}

// TenantDelete - to delete a tenant
func TenantDelete(tenantID string) {
	RunCmd(fmt.Sprintf("/opt/araali/bin/araalictl tenant -op=del -id=%s", tenantID))
}

// GetZones - return zones and apps, use tenant="" by default
func GetZones(full bool, tenant string) []Zone {
	tenantStr := func() string {
		if len(tenant) == 0 {
			return ""
		}
		return "-tenant=" + tenant
	}()
	fullStr := func() string {
		if full {
			return "-full"
		}
		return ""
	}()

	output := RunCmd(fmt.Sprintf("/opt/araali/bin/araalictl api -fetch-zone-apps %s %s", fullStr, tenantStr))
	listOfZones := []Zone{}
	yaml.Unmarshal([]byte(output), &listOfZones)
	return listOfZones
}

// GetLinks - get links for zone, app for tenant
func GetLinks(zone, app, tenant string) []Link {
	tenantStr := func() string {
		if len(tenant) == 0 {
			return ""
		}
		return "-tenant=" + tenant
	}()
	output := RunCmd(fmt.Sprintf("/opt/araali/bin/araalictl api -zone %s -app %s -fetch-links %s", zone, app, tenantStr))
	listOfLinks := []Link{}
	yaml.Unmarshal([]byte(output), &listOfLinks)
	return listOfLinks
}

// FortifyK8sCluster - for tenant
func FortifyK8sCluster(tenant, clusterName string) {
	tenantStr := func() string {
		if len(tenant) == 0 {
			return ""
		}
		return "-tenant=" + tenant
	}()

	if clusterName == "" {
		RunCmd(fmt.Sprintf("/opt/araali/bin/araalictl fortify-k8s %s %s",
			tenantStr, clusterName))
	} else {
		RunCmd(fmt.Sprintf("/opt/araali/bin/araalictl fortify-k8s %s",
			tenantStr))
	}
}

// GetJWT - returns a araali web ui access jwt
func GetJWT(email string) string {
	return RunCmd(fmt.Sprintf("/opt/araali/bin/araalictl token -jwt %s", email))
}

// AlertPage
type AlertPage struct {
	options     string
	PagingToken string
	Alerts      []Link
}

func (alertPage *AlertPage) HasNext() bool {
	if alertPage.PagingToken == "" {
		return false
	}
	return true
}

func (alertPage *AlertPage) NextPage() []Link {
	if alertPage.PagingToken == "" {
		panic("Next page doesn't exist.")
	}
	output := RunCmd(fmt.Sprintf("/opt/araali/bin/araalictl api -fetch-alerts %s -paging-token %s", alertPage.options, alertPage.PagingToken))

	listOfLinks := []Link{}
	yaml.Unmarshal([]byte(output), &listOfLinks)

	alertPage.PagingToken = listOfLinks[len(listOfLinks)-1].PagingToken
	alertPage.Alerts = listOfLinks
	return listOfLinks
}

// GetAlertCard - get AlertCard for tenant.
func GetAlertCard(tenant string) AlertCard {
	tenantStr := func() string {
		if len(tenant) == 0 {
			return ""
		}
		return "-tenant=" + tenant
	}()
	output := RunCmd(fmt.Sprintf("/opt/araali/bin/araalictl api -fetch-alert-card %s", tenantStr))
	alertCard := AlertCard{}
	yaml.Unmarshal([]byte(output), &alertCard)
	return alertCard
}

// GetAlerts - get all alerts for a tenant between specified time.
// tenant: this is optional can be set to emtpy.
// startTime: is optional, should be epoch expressed in seconds. If 0 will be set to currentTime - 1 day.
// endTime: is optional, should be epoch expressed in seconds. If 0 will be set to currentTime.
// count: is optional, should be number of alerts we want to fetch at a time. If 0 will be defaulted 100.
// Sample usage:
// startTime := time.Now().Add(-(3 * araalictl.ONE_DAY)).Unix()
// alertPage := araalictl.GetAlerts("", startTime, 0, 25)
// fmt.Printf("Fetched %d alerts.\n", len(alertPage.Alerts))
// for {
// 	if !alertPage.HasNext() {
// 		fmt.Println("Done fetching!")
// 		break
// 	}
// 	alertPage.NextPage()
// 	fmt.Printf("Fetched %d alerts.\n", len(alertPage.Alerts))
// }
func GetAlerts(tenant string, startTime, endTime int64, count int32) AlertPage {
	tenantStr := func() string {
		if len(tenant) == 0 {
			return ""
		}
		return "-tenant=" + tenant
	}()

	countStr := func() string {
		if count == 0 {
			return ""
		}
		return fmt.Sprint("-count=", count)
	}()

	currentTime := time.Now()
	startTimeStr := func() string {
		if startTime == 0 {
			return fmt.Sprint("-starttime=", currentTime.Add(-ONE_DAY).Unix())
		}
		return fmt.Sprint("-starttime=", startTime)
	}()

	endTimeStr := func() string {
		if endTime == 0 {
			return fmt.Sprint("-endtime=", currentTime.Unix())
		}

		return fmt.Sprint("-endtime=", endTime)
	}()

	output := RunCmd(fmt.Sprintf("/opt/araali/bin/araalictl api -fetch-alerts %s %s %s %s", tenantStr, startTimeStr, endTimeStr, countStr))

	listOfLinks := []Link{}
	yaml.Unmarshal([]byte(output), &listOfLinks)

	return AlertPage{options: fmt.Sprintf(" %s %s %s %s", tenantStr, startTimeStr, endTimeStr, countStr), Alerts: listOfLinks, PagingToken: listOfLinks[len(listOfLinks)-1].PagingToken}
}
