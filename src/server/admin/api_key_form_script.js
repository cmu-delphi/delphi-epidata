// post-processing script for API key registration form submissions
// currently located at:
//   https://script.google.com/u/1/home/projects/1hpgZcxqbeyfJLVEaipNqCJ7ItdkjNu2NsX2IWqpjOd1wZwhCBeKzlCAa/edit


var POST_URL = "https://api.delphi.cmu.edu/epidata/admin/register";
var WEBHOOK_SECRET = "abc";

function onSubmit(e) {


    var form = FormApp.getActiveForm();
    var allResponses = form.getResponses();
    var latestResponse = allResponses[allResponses.length - 1];

    var user_api_key = Math.random().toString(16).substr(2, 18);
    var user_email = latestResponse.getRespondentEmail();

    var payload = {
        'token': WEBHOOK_SECRET,
        'user_api_key': user_api_key,
        'user_email': user_email,
    };

    var options = {
        "method": "post",
        "contentType": "application/json",
        "muteHttpExceptions": true,
        "payload": JSON.stringify(payload)
    };

    Logger.log('Sending registration webhook request.')
    var result = UrlFetchApp.fetch(POST_URL, options);
    console.log(result.getResponseCode());

    if (result.getResponseCode() == 200) {
        Logger.log('Registration successful, sending email');
        MailApp.sendEmail({
            to: user_email,
            subject: "Delphi Epidata API Registration",
            noReply: true,
            body: `Thank you for registering with the Delphi Epidata API.

            Your API key is: ${user_api_key}

            Usage: e.g., http://api.delphi.cmu.edu/epidata/covidcast/meta?token=${user_api_key}

            Best,
            Delphi Team`
        });
    } else if (result.getResponseCode() == 409) {
        Logger.log('Registration was not successful, %s %s', result.getContentText("UTF-8"), result.GetResponseCode);
        MailApp.sendEmail({
            to: user_email,
            subject: "Delphi Epidata API Registration",
            noReply: true,
            body: `
            API Key was not generated.

            This email address is already registered.  Please contact us if you believe this to be in error.

            Best,
            Delphi Team`
        });
    }
};
