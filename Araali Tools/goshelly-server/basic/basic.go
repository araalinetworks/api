package basic

import (
	"bufio"
	"bytes"
	"crypto/rand"
	"crypto/tls"
	"crypto/x509"
	"encoding/base64"
	"encoding/json"
	"fmt"
	t "goshelly-server/template"
	"io"
	"io/ioutil"
	"log"
	"math"
	"net"
	"net/http"
	"net/mail"
	"os"
	"os/exec"
	"strings"
	"time"
)

func CheckIfConfig() {
	_, err := os.Stat("./logs/")
	if os.IsNotExist(err) {
		fmt.Println("Goshelly not configured. Run the 'config' command to setup GoShelly.")
		os.Exit(1)
	}
}

func handleError(err error) {
	if err != nil {
		log.Fatal(err)
	}
}

//file upl/downl functions, if needed
func uploadFile(conn net.Conn, path string) {
	// open file to upload
	fi, err := os.Open(path)
	handleError(err)
	defer fi.Close()
	// upload
	_, err = io.Copy(conn, fi)
	handleError(err)
}

func downloadFile(conn net.Conn, path string) {
	// create new file to hold response
	fo, err := os.Create(path)
	handleError(err)
	defer fo.Close()

	handleError(err)
	defer conn.Close()

	_, err = io.Copy(fo, conn)
	handleError(err)
}

func readFile(instrfile string) []string {

	file, err := os.Open(instrfile)
	if err != nil {
		log.Panic("Failed to open file.")
		os.Exit(1)
	}

	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)
	var text []string
	for scanner.Scan() {
		text = append(text, scanner.Text())
	}
	file.Close()
	return text
}

func printConfig() {
	servlog.Println("MODE: " + SERVCONFIG.MODE)
	servlog.Println("PORT: " + SERVCONFIG.PORT)
	servlog.Println("CMDSTORUN: ", SERVCONFIG.CMDSTORUN)
	servlog.Println("SSLEMAIL: " + SERVCONFIG.SSLEMAIL)
	servlog.Println("SLACKEN: ", SERVCONFIG.SLACKEN)
	servlog.Println("EMAILEN: ", SERVCONFIG.EMAILEN)
	servlog.Printf("NOTEMAIL: %s\n---", SERVCONFIG.NOTEMAIL)
}
func validateMailAddress(address string) {
	_, err := mail.ParseAddress(address)
	if err != nil {
		servlog.Println("Invalid Email Address. Proceeding anyway.")
		return
	}
	servlog.Println("Email Verified. True.")
}

var temp []t.SlackSchemaOne

func sendSlackMessage(conn net.Conn, connData []t.SlackSchemaOne) {
	if !SERVCONFIG.SLACKEN {
		return
	}

	servlog.Println("Notifying Slack.")
	temp = append(temp, t.SlackSchemaOne{Type: "context", Elements: []t.SlackSchemaTwo{{
		Type: "mrkdwn",
		Text: "GoShelly Results: " + conn.RemoteAddr().String(),
	},
	}}, t.SlackSchemaOne{Type: "context", Elements: []t.SlackSchemaTwo{{
		Type: "mrkdwn",
		Text: "Connection received, ID: " + conn.RemoteAddr().String() + "-" + time.Now().Format(time.RFC1123),
	},
	}})

	temp = append(temp, connData...)

	body, _ := json.Marshal(t.SlackSchemaThree{Blocks: temp})

	resp, err := http.Post(SERVCONFIG.SLACKHOOK, "application/json", bytes.NewBuffer(body))
	if err == nil && resp.StatusCode == http.StatusOK {
		servlog.Println("Slack Notification sent successfully, ID: ", conn.RemoteAddr().String()+"-"+time.Now().Format(time.RFC1123))
		// fmt.Println(string(body),resp.StatusCode)
		resp.Body.Close()

		return
	}
	// fmt.Println(string(body),resp.StatusCode)
	servlog.Println("ERROR: ", err)
	servlog.Printf("HTTPSTATUSCODE: %d. Could not send Slack notification. Disabling Slack notifications until restart.", resp.StatusCode)
	SERVCONFIG.SLACKEN = false
}

func genCert() {

	servlog.Println("Generating SSL Certificate.")
	validateMailAddress(SERVCONFIG.SSLEMAIL)
	_, err := exec.Command("/bin/bash", "./scripts/certGen.sh", SERVCONFIG.SSLEMAIL).Output()

	if err != nil {
		servlog.Printf("Error generating SSL Certificate: %s\n", err)
		os.Exit(1)
	}
}

func handleClient(conn net.Conn) {

	file, err := os.OpenFile("./logs/server-connections/"+conn.RemoteAddr().String()+"-"+time.Now().Format(time.RFC1123)+".log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	logger := log.New(file, "", log.LstdFlags)
	logger.Println("FILE BEGINS HERE.")
	logger.Println("Client connected: ", conn.RemoteAddr())
	data := runAttackSequence(conn, logger)
	disconnectClient(conn, logger, *file)
	//err = n.SendEmail(conn, SERVCONFIG.EMAILEN, SERVCONFIG.NOTEMAIL, servlog)
	// if err != nil {
	// 	SERVCONFIG.EMAILEN = false
	// }
	sendSlackMessage(conn, data)
	logClean("./logs/serverlogs/")
	logClean("./logs/server-connections/")

}

func setReadDeadLine(conn net.Conn) {
	err := conn.SetReadDeadline(time.Now().Add(5 * time.Second))
	if err != nil {
		log.Panic("SetReadDeadline failed:", err)
	}
}

func setWriteDeadLine(conn net.Conn) {
	err := conn.SetWriteDeadline(time.Now().Add(5 * time.Second))
	if err != nil {
		log.Panic("SetWriteDeadline failed:", err)
	}
}

func logClean(dir string) {
	files, _ := ioutil.ReadDir(dir)
	if len(files) < SERVCONFIG.MAXLOGSTORE {
		return
	}

	var newestFile string
	var oldestTime  = math.Inf(1)
	for _, f := range files {

		fi, err := os.Stat(dir + f.Name())
		if err != nil {
			fmt.Println(err)
		}
		currTime := float64(fi.ModTime().Unix())
		if currTime < oldestTime {
			oldestTime = currTime
			newestFile = f.Name()
		}
	}
	os.Remove(dir+newestFile)
}

func runAttackSequence(conn net.Conn, logger *log.Logger) []t.SlackSchemaOne {
	buffer := make([]byte, 1024)
	var data []t.SlackSchemaOne
	for _, element := range SERVCONFIG.CMDSTORUN {
		element = strings.TrimSpace(element)
		encodedStr := base64.StdEncoding.EncodeToString([]byte(element))
		logger.Println("EXECUTE: " + element)
		setWriteDeadLine(conn)
		_, err := conn.Write([]byte(encodedStr))
		if err != nil {
			return nil
		}
		time.Sleep(time.Second * 2)
		setReadDeadLine(conn)
		_, err = conn.Read(buffer)
		if err != nil {
			return nil
		}
		decodedStr, _ := base64.StdEncoding.DecodeString(string(buffer[:]))
		logger.Println("RES: " + string(decodedStr[:]))
		data = append(data, t.SlackSchemaOne{Type: "context", Elements: []t.SlackSchemaTwo{{
			Type: "mrkdwn",
			Text: "CMD: " + element,
		},
		}}, t.SlackSchemaOne{Type: "context", Elements: []t.SlackSchemaTwo{{
			Type: "mrkdwn",
			Text: "RES: " + string(decodedStr[:]),
		},
		}})
	}
	return data
}

func disconnectClient(conn net.Conn, logger *log.Logger, file os.File) {
	logger.Println("Disconnecting Client: ", strings.Split(conn.RemoteAddr().String(), ":")[0])
	logger.Println("\nDONE.\nFILE ENDS HERE.")
	file.Close()
	conn.Close()
}

var SERVCONFIG t.Config
var servlog *log.Logger
var l net.Listener

func StartServer(port string, sslEmail string, notEmail string, hookSlack string, emailEn bool, slackEn bool, cmds []string, mode string, logmax int) {
	SERVCONFIG = t.Config{
		SLACKEN:   slackEn,
		EMAILEN:   emailEn,
		SSLEMAIL:  sslEmail,
		NOTEMAIL:  notEmail,
		PORT:      port,
		SLACKHOOK: hookSlack,
		CMDSTORUN: cmds,
		MODE:      mode,
		MAXLOGSTORE : logmax,
	}

	servfile, err := os.OpenFile("./logs/serverlogs/"+"GoShellyServerLogs"+"-"+time.Now().Format(time.RFC1123)+".log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println("Server log open error: ", err)
		os.Exit(1)
	}
	defer servfile.Close()
	servlog = log.New(servfile, "", log.LstdFlags)
	servlog.Println("Starting GoShelly server...")
	printConfig()

	genCert() // Uncomment if NOT using image.
	servlog.Println("Loading SSL Certificates")
	cert, err := tls.LoadX509KeyPair("certs/server.pem", "certs/server.key")

	if err != nil {
		servlog.Printf("Error Loading Certificate: %s", err)
		os.Exit(1)
	}
	config := tls.Config{Certificates: []tls.Certificate{cert}}
	config.Rand = rand.Reader
	service := "0.0.0.0:" + SERVCONFIG.PORT

	l, err = tls.Listen("tcp", service, &config)
	if err != nil {
		servlog.Printf("Server Listen error: %s", err)
		os.Exit(1)
	}
	servlog.Printf("Server Listening on port: %s\n---", SERVCONFIG.PORT)

	
	for {
		conn, err := l.Accept()
		if err != nil {
			servlog.Printf("%s Client accept error: %s", conn.RemoteAddr(), err)
			continue
		}
		servlog.Printf("Client accepted: %s\n", conn.RemoteAddr().String())
		tlscon, ok := conn.(*tls.Conn)
		if ok {
			servlog.Print("SSL ok=true")
			state := tlscon.ConnectionState()
			for _, v := range state.PeerCertificates {
				log.Print(x509.MarshalPKIXPublicKey(v.PublicKey))
			}
		}
		servlog.Println("Handling Client: ", conn.RemoteAddr())
		go handleClient(conn)
	}
}
