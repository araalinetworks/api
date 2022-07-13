package goshellyserverapi

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	b "goshelly-server/basic"
	t "goshelly-server/template"
	"io/ioutil"
	"strconv"

	// "io/ioutil"
	"net/http"
	"net/mail"
	"os"
	"strings"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/gin-gonic/gin"
	"golang.org/x/crypto/bcrypt"
)

var r *gin.Engine

const DOMAIN = "http://localhost:9000"
const SECRETKEY = "THIS IS A SECRET KEY, CHANGE TO SOMETHING MORE SECURE." //change this

func initServerApi() {
	r = gin.Default()
	r.LoadHTMLGlob("html/*.html")
	os.MkdirAll("./clients/", os.ModePerm)
	os.MkdirAll("./logs/GoShellyServer-api-logs/", os.ModePerm)
	apifile, err := os.OpenFile("./logs/GoShellyServer-api-logs/"+"api-log"+"-"+time.Now().Format(time.RFC1123)+".log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Printf("Api log open error: %s. Logs unavailable.", err)
	}
	if err == nil {
		gin.DefaultWriter = apifile
	}

	b.LogClean("./logs/GoShellyServer-api-logs/", b.SERVCONFIG.SERVMAXLOGSTORE)
	///NOTE: 100 is a random hardcoded value, this function call decides that the max number of logs for the api server cannot
	//excede 100
}

func test() {
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "pong",
		})
	})
}

func validateMailAddress(address string) bool {
	_, err := mail.ParseAddress(address)
	return err == nil
}
func addUser() {
	r.POST("/signup/", func(c *gin.Context) {
		var user t.User
		c.BindJSON(&user)
		if !validateMailAddress(user.EMAIL) {
			c.JSON(http.StatusForbidden, gin.H{"message": "Email address provided is incorrect."})
			return
		}
		if b.FindUser(strings.TrimSpace(user.EMAIL)) {
			c.JSON(http.StatusForbidden, gin.H{"message": "User already exists with this email. Try a different email."})
			return
		}
		user.PASSWORD, _ = bcrypt.GenerateFromPassword([]byte(user.PASSWORD), 12)
		os.MkdirAll("./clients/"+user.EMAIL+"/logs/", os.ModePerm)
		f, err := os.Create("./clients/" + user.EMAIL + "/" + "user.json")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Could not create user."})
			return
		}
		f.Close()
		file, err := json.MarshalIndent(t.User{
			NAME:     base64.StdEncoding.EncodeToString([]byte(user.NAME)),
			EMAIL:    base64.StdEncoding.EncodeToString([]byte(user.EMAIL)),
			PASSWORD: user.PASSWORD,
		}, "", " ")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Could not create user."})
			return
		}
		err = ioutil.WriteFile("./clients/"+user.EMAIL+"/user.json", file, 0644)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Could not create user."})
			return
		}

		c.JSON(http.StatusCreated, gin.H{"message": "User created."})
	})
}

func removeUser() {
	r.DELETE("/delete/", func(c *gin.Context) {
		var user t.LoggedUser
		c.BindJSON(&user)
		// fmt.Println(strings.TrimSpace(user.EMAIL))
		if !b.FindUser(strings.TrimSpace(user.EMAIL)) {
			c.JSON(http.StatusNotFound, gin.H{"message": "User not found."})
			return
		}
		if !authToken(user) {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Permission denied. Ensure you are logged in."})
			return
		}
		os.Remove("./clients/" + user.EMAIL + "/")
		c.JSON(http.StatusOK, gin.H{"message": "User Deleted."})
	})
}

func loginUser() {
	r.POST("/login/", func(c *gin.Context) {
		var user t.LoginUser
		c.BindJSON(&user)
		if !b.FindUser(strings.TrimSpace(user.EMAIL)) {
			c.JSON(http.StatusNotFound, gin.H{"message": "Incorrect credentials or user does not exist.", "token": ""})
			return
		}

		var temp t.User
		file, _ := ioutil.ReadFile("./clients/" + user.EMAIL + "/user.json")
		err := json.Unmarshal([]byte(file), &temp)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Could not login user. Service unavailable.",
				"token": ""})
			return
		}
		if err := bcrypt.CompareHashAndPassword(temp.PASSWORD, user.PASSWORD); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"message": "Invalid Credentials.",
				"token":   "",
			})
			return
		}
		claims := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.StandardClaims{
			Issuer:    "GoShelly Admin",
			IssuedAt:  time.Now().Unix(),
			ExpiresAt: time.Now().Add(time.Hour * 1).Unix(),
			Audience:  user.EMAIL,
		})
		token, err := claims.SignedString([]byte(SECRETKEY))
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"message": "Service unavailable. Could not login.",
				"token":   "",
			})
			return
		}
		c.JSON(http.StatusOK, gin.H{
			"message": "Login Successful.",
			"token":   token,
		})
	})
}

func authToken(user t.LoggedUser) bool {
	claims := jwt.MapClaims{}
	_, err := jwt.ParseWithClaims(user.TOKEN, claims, func(token *jwt.Token) (interface{}, error) {
		return []byte(SECRETKEY), nil
	})
	if err != nil || !claims.VerifyAudience(user.EMAIL, true) ||
		!claims.VerifyIssuer("GoShelly Admin", true) || !claims.VerifyExpiresAt(time.Now().Unix(), true) { //} || claims["sub"].(string) != user.NAME {
		return false
	}
	return true
}

func checkCurrentToken() {
	r.POST("/auth/", func(c *gin.Context) {
		var user t.LoggedUser
		c.BindJSON(&user)

		if !b.FindUser(strings.TrimSpace(user.EMAIL)) {
			c.JSON(http.StatusNotFound, gin.H{"message": "Incorrect credentials or user does not exist.", "token": user.TOKEN})
			return
		}
		if !authToken(user) {
			c.JSON(http.StatusUnauthorized, gin.H{
				"message": "Invalid Credentials.",
				"token":   user.TOKEN,
			})
			return
		}
		c.JSON(http.StatusAccepted, gin.H{
			"message": "Credentials=Valid",
			"token":   user.TOKEN,
		})
	})
}

func returnUserLogs() {
	r.POST("/list/", func(c *gin.Context) {
		var user t.LoggedUser
		c.BindJSON(&user)
		if !b.FindUser(strings.TrimSpace(user.EMAIL)) {
			c.JSON(http.StatusNotFound, gin.H{"message": "No logs found for current logged in user."})
			return
		}
		if !authToken(user) {
			c.JSON(http.StatusUnauthorized, gin.H{
				"message": "Invalid Credentials.",
			})
			return
		}
		var returnMsg strings.Builder

		files, err := ioutil.ReadDir("./clients/" + user.EMAIL + "/logs/")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Could not get logs. Try again later."})
			return
		}
		returnMsg.WriteString("ID\t\t\tFILENAME\n")
		for id, file := range files {
			returnMsg.WriteString(strconv.Itoa(id+1) + "-->" + strings.ReplaceAll(file.Name(), ".log", "") + "\n")
		}
		c.JSON(http.StatusOK, gin.H{"message": returnMsg.String()})
	})

}

func createLink() {
	r.POST("/link/", func(c *gin.Context) {
		var user t.UserLinks
		c.BindJSON(&user)
		if !b.FindUser(user.EMAIL) {
			c.JSON(http.StatusNotFound, gin.H{"message": "Incorrect credentials or user does not exist."})
			return
		}
		if !authToken(t.LoggedUser{
			TOKEN: user.TOKEN,
			EMAIL: user.EMAIL,
		}) {
			c.JSON(http.StatusBadRequest, gin.H{"message": "Permission denied. Please log in again."})
			return
		}

		link := DOMAIN + "/logs/" + user.EMAIL + "/" + strconv.Itoa(user.LOGID) + "/"
		c.JSON(http.StatusOK, gin.H{"message": link})
	})
}

func hostLog() {

	r.GET("/logs/:userid/:id", func(c *gin.Context) {
		userid := c.Param("userid")
		id, err := strconv.Atoi(c.Param("id"))

		if err != nil || userid == "" || id < 1 || id > b.SERVCONFIG.CLIMAXLOGSTORE {
			c.HTML(http.StatusNotFound, "404.html", gin.H{
				"message": "Not found.",
			})
			return
		}
		files, err := ioutil.ReadDir("./clients/" + userid + "/logs/")
		if err != nil {
			c.HTML(http.StatusInternalServerError, "oops.html", gin.H{
				"message": "InternalServerError",
			})
			return
		}
		if len(files) == 0 {
			c.HTML(http.StatusNotFound, "404.html", gin.H{
				"message": "Not found.",
			})
			return
		}

		message, err := ioutil.ReadFile("./clients/" + userid + "/logs/" + files[id-1].Name())
		if err != nil {
			c.HTML(http.StatusInternalServerError, "oops.html", gin.H{
				"message": "InternalServerError",
			})
		}
		c.String(http.StatusOK, string(message))
	})
}

func startAPI() {
	initServerApi()
	removeUser()
	checkCurrentToken()
	addUser()
	loginUser()
	returnUserLogs()
	createLink()
	hostLog()
	test()
}

func BeginAPI(APIHOSTPORT string) {
	startAPI()
	r.Run(":" + APIHOSTPORT)
}
