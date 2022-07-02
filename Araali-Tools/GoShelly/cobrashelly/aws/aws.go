package aws

import (
	t "cobrashelly/template"
	"log"
	"net"
	"time"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/ses"
)


func SendEmail(conn net.Conn, EMAILEN bool, NOTEMAIL string,servlog *log.Logger) error{
	if !EMAILEN {
		return nil 
	}
    servlog.Println("Notifying email.")
	TEMPLATE := t.Emailtemp{
		SENDER: "support@araalinetworks.com",
		RECIPIENT: NOTEMAIL,
		SUBJECT: "Araali GoShelly Results",
		HTMLBODY: "",
 		TEXTBODY: "A new connection received was detected by GoShelly with Id: " + conn.RemoteAddr().String() + "-" + time.Now().Format(time.RFC1123),
		CHARSET: "UTF-8",
	}



	sess, err := session.NewSession(&aws.Config{
        Region:aws.String("us-west-2")},
    )
	if err != nil{
		servlog.Println("Email sending failed. Disabling email notifications until restart.")
		return err
	}
    
    svc := ses.New(sess)
    input := &ses.SendEmailInput{
        Destination: &ses.Destination{
            CcAddresses: []*string{
            },
            ToAddresses: []*string{
                aws.String(TEMPLATE.RECIPIENT),
            },
        },
        Message: &ses.Message{
            Body: &ses.Body{
                Html: &ses.Content{
                    Charset: aws.String(TEMPLATE.CHARSET),
                    Data:    aws.String(TEMPLATE.HTMLBODY),
                },
                Text: &ses.Content{
                    Charset: aws.String(TEMPLATE.CHARSET),
                    Data:    aws.String(TEMPLATE.TEXTBODY),
                },
            },
            Subject: &ses.Content{
                Charset: aws.String(TEMPLATE.CHARSET),
                Data:    aws.String(TEMPLATE.SUBJECT),
            },
        },
        Source: aws.String(TEMPLATE.SENDER),
            // Uncomment to use a configuration set
            //ConfigurationSetName: aws.String(ConfigurationSet),
    }

    // Attempt to send the email.
    _, err = svc.SendEmail(input)
    
    // Display error messages if they occur.
    if err != nil {
        if aerr, ok := err.(awserr.Error); ok {
            switch aerr.Code() {
            case ses.ErrCodeMessageRejected:
                servlog.Println(ses.ErrCodeMessageRejected, aerr.Error())
            case ses.ErrCodeMailFromDomainNotVerifiedException:
                servlog.Println(ses.ErrCodeMailFromDomainNotVerifiedException, aerr.Error())
            case ses.ErrCodeConfigurationSetDoesNotExistException:
                servlog.Println(ses.ErrCodeConfigurationSetDoesNotExistException, aerr.Error())
            default:
                servlog.Println(aerr.Error())
            }
        } else {
            servlog.Println(err.Error())
        }
		servlog.Println("Email sending failed. Disabling email notification till restart.")
        return err
    }
    
    servlog.Println("Email notification sent for connection Id: ", conn.RemoteAddr().String() + "-" + time.Now().Format(time.RFC1123))
	return nil
}