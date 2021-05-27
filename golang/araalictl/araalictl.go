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

// Araalictl path
var ActlPath = "/opt/araali/bin/araalictl"

// CommandDebug - logs every command that is executed
var CommandDebug = false

// RunControlOut takes a command and runs it, control is for whether to exit, allows output to go to stdout
func RunControlOut(cmdArgs []string, user string, exitOnFailure bool, out *bytes.Buffer, in *bytes.Buffer) error {
	if CommandDebug {
		fmt.Println(cmdArgs, user, exitOnFailure)
	}
	cmd := exec.Command(cmdArgs[0], cmdArgs[1:]...)
	cmd.Env = os.Environ()
	if len(user) != 0 {
		cmd.SysProcAttr = &syscall.SysProcAttr{}
		uids, _ := RunControl([]string{"id", "-u", user}, "", true, "")
		uid, _ := strconv.Atoi(strings.TrimSpace(uids))
		gids, _ := RunControl([]string{"id", "-g", user}, "", true, "")
		gid, _ := strconv.Atoi(strings.TrimSpace(gids))
		cmd.SysProcAttr.Credential = &syscall.Credential{Uid: uint32(uid), Gid: uint32(gid)}
	}

	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if out != nil {
		cmd.Stdout = out
		//cmd.Stderr = out // comment to not capture stderr
	}
	if in != nil {
		cmd.Stdin = in
	}

	if err := cmd.Run(); err != nil {
		if exitOnFailure {
			fmt.Fprintln(os.Stderr, strings.Join(cmdArgs, " ")+": "+fmt.Sprint(err)+": "+out.String())
			os.Exit(1)
		} else {
			return fmt.Errorf(strings.Join(cmdArgs, " ") + ": " + fmt.Sprint(err) + ": " + out.String() + "\n")
		}
	}
	return nil
}

// RunControl takes a command and runs it, control is for whether to exit
func RunControl(cmdArgs []string, user string, exitOnFailure bool, pipeInput string) (string, error) {
	var out bytes.Buffer

	if pipeInput != "" {
		in := bytes.Buffer{}
		in.Write([]byte(pipeInput))
		err := RunControlOut(cmdArgs, user, exitOnFailure, &out, &in)
		if err == nil {
			return out.String(), nil
		}
		return "", err
	} else {
		err := RunControlOut(cmdArgs, user, exitOnFailure, &out, nil)
		if err == nil {
			return out.String(), nil
		}
		return "", err
	}
}

// RunStrControl takes a command string and runs it, control is for whether to exit
func RunStrControl(cmdstr, user string, exitOnFailure bool, pipeInput string) (string, error) {
	return RunControl([]string{"sh", "-c", cmdstr}, user, exitOnFailure, pipeInput)
}

// RunAs - Run cmdstr as user
func RunAs(cmdstr, user string, pipeInput string) (string, error) {
	return RunStrControl(cmdstr, user, false, pipeInput)
}

// RunCmd - Run cmdstr and collect/return output
func RunCmd(cmdstr string) (string, error) {
	return RunAs(cmdstr, "", "")
}

func RunCmdWithInput(cmdstr string, pipeInput string) (string, error) {
	return RunAs(cmdstr, "", pipeInput)
}

type Zone struct {
	ZoneName string `yaml:"zone_name"`
	Apps     []App
}

type App struct {
	ZoneName      string
	AppName       string          `yaml:"app_name"`
	Links         []Link          `yaml:"links,omitempty"`
	DefinedCounts DirectionCounts `yaml:"defined_policies,omitempty"`
	DeniedCounts  DirectionCounts `yaml:"denied_policies,omitempty"`
	AlertCounts   DirectionCounts `yaml:"alerts,omitempty"`
	ServiceCounts DirectionCounts `yaml:"services,omitempty"`
	ComputeCounts ComputeCount    `yaml:"compute,omitempty"`
	AraaliUrl     string          `yaml:"araali_url,omitempty"`
}

func (app *App) Refresh() error {
	links, err := GetLinks(app.ZoneName, app.AppName, "")
	app.Links = links
	return err
}

func (app *App) Commit() (string, error) {
	links := []Link{}
	for _, l := range app.Links {
		if l.NewState != "" {
			links = append(links, l)
		}
	}
	return UpdateLinks(app.ZoneName, app.AppName, "", links)
}

type DirectionCounts struct {
	Total            uint64 `yaml:"total,omitempty"`
	Ingress          uint64 `yaml:"ingress,omitempty"`
	PerimeterIngress uint64 `yaml:"perimeter_ingress,omitempty"`
	Internal         uint64 `yaml:"internal,omitempty"`
	Egress           uint64 `yaml:"egress,omitempty"`
	PerimeterEgress  uint64 `yaml:"perimeter_egress,omitempty"`
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

func (link *Link) Accept() {
	link.NewState = "DEFINED_POLICY"
}

func (link *Link) Snooze() {
	link.NewState = "SNOOZED_POLICY"
}

func (link *Link) Deny() {
	link.NewState = "DENIED_POLICY"
}

// AlertInfo object
type AlertInfo struct {
	CommunicationAlertType string `yaml:"communication_alert_type,omitempty"`
	ProcessAlertType       string `yaml:"process_alert_type,omitempty"`
	ReOpenCount            uint32 `yaml:"reopen_count,omitempty"`
	Status                 string `yaml:"status,omitempty"`
}

// Reset araalictl path to new value
func SetAraalictlPath(newPath string) {
	ActlPath = newPath
}

// Authorize araalictl
func Authorize(token string, asRoot bool) (string, error) {
	cmd := fmt.Sprintf("%s authorize -token=- -local", ActlPath)
	if asRoot {
		cmd = "sudo " + cmd
	}
	return RunCmdWithInput(cmd, token)
}

// DeAuthorize araalictl
func DeAuthorize(asRoot bool) (string, error) {
	cmd := fmt.Sprintf("%s authorize -clean", ActlPath)
	if asRoot {
		cmd = "sudo " + cmd
	}
	return RunCmd(cmd)
}

// TenantCreate - to create a tenant
func TenantCreate(userEmail, tenantName, UserName string) (string, error) {
	return RunCmd(fmt.Sprintf("%s tenant -op=add -name=\"%s\" -user-email=%s -user-name=\"%s\"",
		ActlPath, tenantName, userEmail, UserName))
}

// TenantDelete - to delete a tenant
func TenantDelete(tenantID string) (string, error) {
	return RunCmd(fmt.Sprintf("%s tenant -op=del -id=%s", ActlPath, tenantID))
}

// TenantAddUser - to add a user to a tenant
func TenantAddUser(tenantID, userEmail, userName string) (string, error) {
	return RunCmd(fmt.Sprintf("%s tenant -op=add-user -id=\"%s\" -user-email=%s -user-name=\"%s\"",
		ActlPath, tenantID, userEmail, userName))
}

// TenantDeleteUser - to delete a user from a tenant
func TenantDeleteUser(tenantID, userEmail, userName string) (string, error) {
	return RunCmd(fmt.Sprintf("%s tenant -op=del-user -id=\"%s\" -user-email=%s -user-name=\"%s\"",
		ActlPath, tenantID, userEmail, userName))
}

// GetZones - return zones and apps, use tenant="" by default
func GetZones(full bool, tenant string) ([]Zone, error) {
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

	output, err := RunCmd(fmt.Sprintf("%s api -fetch-zone-apps %s %s", ActlPath, fullStr, tenantStr))
	if err != nil {
		return []Zone{}, err
	}
	listOfZones := []Zone{}
	yaml.Unmarshal([]byte(output), &listOfZones)
	return listOfZones, nil
}

// GetLinks - get links for zone, app for tenant
func GetLinks(zone, app, tenant string) ([]Link, error) {
	tenantStr := func() string {
		if len(tenant) == 0 {
			return ""
		}
		return "-tenant=" + tenant
	}()
	output, err := RunCmd(fmt.Sprintf("%s api -zone %s -app %s -fetch-links %s", ActlPath, zone, app, tenantStr))
	if err != nil {
		return []Link{}, err
	}
	listOfLinks := []Link{}
	yaml.Unmarshal([]byte(output), &listOfLinks)
	return listOfLinks, nil
}

// UpdateLinks - update links for an app
func UpdateLinks(zone, app, tenant string, links []Link) (string, error) {
	tenantStr := func() string {
		if len(tenant) == 0 {
			return ""
		}
		return "-tenant=" + tenant
	}()
	input, _ := yaml.Marshal(links)
	return RunCmdWithInput(fmt.Sprintf("%s api -zone %s -app %s -update-links %s", ActlPath, zone, app, tenantStr), string(input))
}

// FortifyK8sCluster - for tenant
func FortifyK8sCluster(tenant, clusterName string, force bool) (string, error) {
	tenantStr := func() string {
		if len(tenant) == 0 {
			return ""
		}
		return "-tenant=" + tenant
	}()
	if force {
		return RunCmd(fmt.Sprintf("%s fortify-k8s -force %s %s", ActlPath, tenantStr, clusterName))
	}
	return RunCmd(fmt.Sprintf("%s fortify-k8s %s %s", ActlPath, tenantStr, clusterName))
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

func (alertPage *AlertPage) NextPage() ([]Link, error) {
	if alertPage.PagingToken == "" {
		panic("Next page doesn't exist.")
	}
	output, err := RunCmd(fmt.Sprintf("%s api -fetch-alerts %s -paging-token %s", ActlPath, alertPage.options, alertPage.PagingToken))
	listOfLinks := []Link{}
	if err != nil {
		return listOfLinks, err
	}
	yaml.Unmarshal([]byte(output), &listOfLinks)

	alertPage.PagingToken = listOfLinks[len(listOfLinks)-1].PagingToken
	alertPage.Alerts = listOfLinks
	return listOfLinks, err
}

// GetAlertCard - get AlertCard for tenant.
func GetAlertCard(tenant string) (AlertCard, error) {
	tenantStr := func() string {
		if len(tenant) == 0 {
			return ""
		}
		return "-tenant=" + tenant
	}()
	output, err := RunCmd(fmt.Sprintf("%s api -fetch-alert-card %s", ActlPath, tenantStr))
	alertCard := AlertCard{}
	if err != nil {
		return alertCard, err
	}
	yaml.Unmarshal([]byte(output), &alertCard)
	return alertCard, err
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
func GetAlerts(tenant string, startTime, endTime int64, count int32) (AlertPage, error) {
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

	output, err := RunCmd(fmt.Sprintf("%s api -fetch-alerts %s %s %s %s", ActlPath, tenantStr, startTimeStr, endTimeStr, countStr))
	if err != nil {
		return AlertPage{}, err
	}

	listOfLinks := []Link{}
	yaml.Unmarshal([]byte(output), &listOfLinks)

	return AlertPage{options: fmt.Sprintf(" %s %s %s %s", tenantStr, startTimeStr, endTimeStr, countStr), Alerts: listOfLinks, PagingToken: listOfLinks[len(listOfLinks)-1].PagingToken}, nil
}
