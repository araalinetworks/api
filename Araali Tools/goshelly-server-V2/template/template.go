package template

type Emailtemp struct {
	SENDER    string
	RECIPIENT string
	SUBJECT   string
	HTMLBODY  string
	TEXTBODY  string
	CHARSET   string
}

type Config struct {
	SLACKEN         bool
	EMAILEN         bool
	SSLEMAIL        string
	NOTEMAIL        string
	PORT            string
	SLACKHOOK       string
	CMDSTORUN       []string
	MODE            string
	SERVMAXLOGSTORE int
	CLIMAXLOGSTORE  int
}

type LoginUser struct {
	EMAIL    string `json:"email"`
	PASSWORD []byte `json:"pwd"`
}
type User struct {
	NAME     string `json:"name"`
	EMAIL    string `json:"email"`
	PASSWORD []byte `json:"pwd"`
}

type LoggedUser struct {
	// NAME        string `json:"name"`
	EMAIL string `json:"email"`
	TOKEN string `json:"token"`
}

type UserLinks struct{
	EMAIL string `json:"email"`
	TOKEN string `json:"token"`
	LOGID int  `json:"logid"`
	
}

type Token struct {
	TOKEN string `json:"token"`
}

type SlackSchemaOne struct {
	Type     string           `json:"type"`
	Elements []SlackSchemaTwo `json:"elements"`
}

type SlackSchemaTwo struct {
	Type string `json:"type"`
	Text string `json:"text"`
}

type SlackSchemaThree struct {
	Blocks []SlackSchemaOne `json:"blocks"`
}
