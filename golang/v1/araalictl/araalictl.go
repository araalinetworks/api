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

type TenantUser struct {
	Id        string `yaml:"id" json:"id"`
	Name      string `yaml:"name" json:"name"`
	UserEmail string `yaml:"useremail" json:"useremail"`
	UserName  string `yaml:"username" json:"username"`
	Role      string `yaml:"role" json:"role"`
}

// FortifyHelmValues
type FortifyAraaliHelmValues struct {
	WorkloadId   string `yaml:"workload_id" json:"workload_id"`
	ClusterName  string `yaml:"cluster_name" json:"cluster_name"`
	Fog          string `yaml:"fog" json:"fog"`
	Zone         string `yaml:"zone" json:"zone"`
	App          string `yaml:"app" json:"app"`
	Enforce      bool   `yaml:"enforce" json:"enforce"`
	Upgrade      bool   `yaml:"upgrade" json:"upgrade"`
	AutoK8SImage string `yaml:"autok8s_image" json:"autok8s_image"`
	FwImage      string `yaml:"fw_image" json:"fw_image"`
	FwInitImage  string `yaml:"fw_init_image" json:"fw_init_image"`
}

type FortifyHelmValues struct {
	AHV FortifyAraaliHelmValues `yaml:"araali" json:"araali"`
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

type Vulnerability struct {
	PackageName string   `yaml:"package_name"`
	CveId       []string `yaml:"cve_id"`
	Severity    string   `yaml:"severity"`
}

type Compute struct {
	Name                string          `yaml:"name"`
	IpAddress           string          `yaml:"ip_address"`
	Uuid                string          `yaml:"uuid"`
	Image               string          `yaml:"image"`
	Zone                string          `yaml:"zone"`
	Apps                []App           `yaml:"apps"`
	Processes           []string        `yaml:"processes"`
	State               string          `yaml:"state"`
	AssetType           string          `yaml:"asset_type"`
	ProcessCapabilities []string        `yaml:"process_capabilities"`
	IpAddresses         []string        `yaml:"ip_addresses"`
	OriginalUuid        string          `yaml:"original_uuid`
	Vulnerabilities     []Vulnerability `yaml:"vulnerabilities"`
	Mode                string          `yaml:"mode"`
	OsName              string          `yaml:"os_name"`
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

// InsightCounts
type Insight struct {
	InsightType string `yaml:"insighttype" json:"insighttype"`
	Url         string `yaml:"url" json:"url"`
	Count       int    `yaml:"count" json:"count"`
}

// Generate tenant string for command line args
func getTenantStr(tenant string) string {
	if len(tenant) == 0 {
		return ""
	}
	return "-tenant=" + tenant
}

// Reset araalictl path to new value
func SetAraalictlPath(newPath string) {
	ActlPath = newPath
}

// Authorize araalictl
func Authorize(emailid, token string, asRoot bool) (string, error) {
	cmd := fmt.Sprintf("%s authorize -token=- -local %s", ActlPath, emailid)
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

//
// Tenant and User Update Operations
//

// TenantCreate - returns tenant-id
func TenantCreate(name, adminName, adminEmail string, freemium bool) (string, error) {
	if len(adminEmail) == 0 {
		// TODO: validate the email address format
		return "", fmt.Errorf("invalid adminEmail (%v)", adminEmail)
	}
	resp, err := RunCmd(fmt.Sprintf(
		"%s tenant -api -op=add -name=\"%s\" -user-email=\"%s\" -user-name=\"%s\"",
		ActlPath, name, adminEmail, adminName))
	if err != nil {
		return "", err
	}
	var tu TenantUser
	err = yaml.Unmarshal([]byte(resp), &tu)
	if err != nil {
		return "", err
	}
	return tu.Id, nil
}

// TenantDelete
func TenantDelete(tenantID string) error {
	if len(tenantID) == 0 {
		return fmt.Errorf("invalid tenantid (%v)", tenantID)
	}
	_, err := RunCmd(fmt.Sprintf(
		"%s tenant -api -op=del -id=\"%s\"", ActlPath, tenantID))
	if err != nil {
		return err
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
	_, err := RunCmd(fmt.Sprintf(
		"%s tenant -api -op=add-user -id=\"%s\" -user-email=\"%s\" -user-name=\"%s\" -roles=\"%s\"",
		ActlPath, tenantID, userEmail, userName, role))
	return err
}

// UserDelete
func UserDelete(tenantID, userEmail string) error {
	if len(tenantID) == 0 {
		return fmt.Errorf("invalid tenantid (%v)", tenantID)
	} else if len(userEmail) == 0 {
		return fmt.Errorf("invalid user email (%v)", userEmail)
	}
	_, err := RunCmd(fmt.Sprintf("%s tenant -api -op=del-user -id=\"%s\" -user-email=\"%s\"",
		ActlPath, tenantID, userEmail))
	return err
}

// FortifyK8SGenerateHelm - Generates values.yaml for araali fortification helm chart
func FortifyK8SGenerateHelm(tenantID, clusterName string) (*FortifyHelmValues, error) {
	if tenantID == "" {
		return nil, fmt.Errorf("invalid tenantid (%v)", tenantID)
	} else if clusterName == "" {
		return nil, fmt.Errorf("invalid clusterName (%v)", clusterName)
	}

	output, err := RunCmd(fmt.Sprintf(
		"%s fortify-k8s -tenant=%s -tags=zone=%s -out=helm %s",
		ActlPath, tenantID, clusterName, clusterName))
	if err != nil {
		return nil, fmt.Errorf("failed to generate helm (err: %v/(%v))", err, output)
	}

	if len(strings.TrimSpace(output)) == 0 {
		return nil, fmt.Errorf("failed to generate helm emtpy output %v", output)
	}

	var hv FortifyHelmValues
	err = yaml.Unmarshal([]byte(output), &hv)
	if err != nil {
		return nil, fmt.Errorf("failed unmarshall helm (err: %v)", err)
	}
	return &hv, nil
}

// GetZones - return zones and apps, use tenant="" by default
func GetZones(full bool, tenant string) ([]Zone, error) {
	fullStr := func() string {
		if full {
			return "-full"
		}
		return ""
	}()

	output, err := RunCmd(fmt.Sprintf("%s api -fetch-zone-apps %s %s", ActlPath, fullStr, getTenantStr(tenant)))
	if err != nil {
		return []Zone{}, err
	}
	listOfZones := []Zone{}
	yaml.Unmarshal([]byte(output), &listOfZones)
	return listOfZones, nil
}

// GetCompute - return VMs and containers for given zone/app with vulnerability info
func GetCompute(zone, app, tenant string) ([]Compute, error) {
	output, err := RunCmd(fmt.Sprintf("%s api -zone=%s -app=%s -fetch-compute %s", ActlPath, zone, app, getTenantStr(tenant)))
	if err != nil {
		return []Compute{}, err
	}
	listOfCompute := []Compute{}
	yaml.Unmarshal([]byte(output), &listOfCompute)
	return listOfCompute, nil
}

// GetLinks - get links for zone, app for tenant
func GetLinks(zone, app, tenant string) ([]Link, error) {
	output, err := RunCmd(fmt.Sprintf("%s api -zone %s -app %s -fetch-links %s", ActlPath, zone, app, getTenantStr(tenant)))
	if err != nil {
		return []Link{}, err
	}
	listOfLinks := []Link{}
	yaml.Unmarshal([]byte(output), &listOfLinks)
	return listOfLinks, nil
}

// UpdateLinks - update links for an app
func UpdateLinks(zone, app, tenant string, links []Link) (string, error) {
	input, _ := yaml.Marshal(links)
	return RunCmdWithInput(fmt.Sprintf("%s api -zone %s -app %s -update-links %s", ActlPath, zone, app, getTenantStr(tenant)), string(input))
}

// FortifyK8sCluster - for tenant
func FortifyK8sCluster(tenant, clusterName string, force bool) (string, error) {
	if force {
		return RunCmd(fmt.Sprintf("%s fortify-k8s -force %s %s", ActlPath, getTenantStr(tenant), clusterName))
	}
	return RunCmd(fmt.Sprintf("%s fortify-k8s %s %s", ActlPath, getTenantStr(tenant), clusterName))
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
	if err != nil || len(listOfLinks) == 0 {
		alertPage.PagingToken = ""
		return listOfLinks, err
	}
	yaml.Unmarshal([]byte(output), &listOfLinks)

	alertPage.PagingToken = listOfLinks[len(listOfLinks)-1].PagingToken
	alertPage.Alerts = listOfLinks
	return listOfLinks, err
}

// GetAlertCard - get AlertCard for tenant.
func GetAlertCard(tenant string) (AlertCard, error) {
	output, err := RunCmd(fmt.Sprintf("%s api -fetch-alert-card %s", ActlPath, getTenantStr(tenant)))
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
func GetAlerts(tenant string, startTime, endTime int64, count int32, fetchAll bool) (AlertPage, error) {
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

	fetchAllStr := func() string {
		return fmt.Sprint("-all=", fetchAll)
	}()

	output, err := RunCmd(fmt.Sprintf("%s api -fetch-alerts %s %s %s %s %s", ActlPath, getTenantStr(tenant), startTimeStr, endTimeStr, countStr, fetchAllStr))
	if err != nil {
		return AlertPage{}, err
	}

	listOfLinks := []Link{}
	yaml.Unmarshal([]byte(output), &listOfLinks)

	pagingToken := ""
	if len(listOfLinks) != 0 {
		pagingToken = listOfLinks[len(listOfLinks)-1].PagingToken
	}
	return AlertPage{options: fmt.Sprintf(" %s %s %s %s", getTenantStr(tenant), startTimeStr, endTimeStr, countStr), Alerts: listOfLinks, PagingToken: pagingToken}, nil
}

// GetInsights
func GetInsights(tenantID string) ([]Insight, error) {
	output, err := RunCmd(fmt.Sprintf(
		"%s api %s -fetch-insights", ActlPath, getTenantStr(tenantID)))
	if err != nil {
		return nil, fmt.Errorf("failed to fetch insights (%v)", err)
	}
	listOfInsights := []Insight{}
	yaml.Unmarshal([]byte(output), &listOfInsights)
	return listOfInsights, nil
}
