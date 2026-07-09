// post-processing script for API key registration form submissions
// currently located at:
//   https://script.google.com/u/1/home/projects/1hpgZcxqbeyfJLVEaipNqCJ7ItdkjNu2NsX2IWqpjOd1wZwhCBeKzlCAa/edit


var POST_URL = "https://api.delphi.cmu.edu/epidata/admin/register";
var REPLACE_URL = "https://api.delphi.cmu.edu/epidata/admin/replace_key";
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

            For usage information, see the API Keys section of the documentation: https://cmu-delphi.github.io/delphi-epidata/api/api_keys.html

            We strongly suggest you subscribe to our API mailing list to make sure you are informed on important topics, like announcements of API changes, details of updates to data, and unexpected downtime or other problems: https://lists.andrew.cmu.edu/mailman/listinfo/delphi-covidcast-api

            Best,
            Delphi Team`
        });
    } else if (result.getResponseCode() == 409) {
        Logger.log('Email already registered, replacing key for %s', user_email);
        var new_api_key = Math.random().toString(16).substr(2, 18);
        var replacePayload = {
            'token': WEBHOOK_SECRET,
            'user_api_key': new_api_key,
            'user_email': user_email,
        };
        var replaceOptions = {
            "method": "post",
            "contentType": "application/json",
            "muteHttpExceptions": true,
            "payload": JSON.stringify(replacePayload)
        };
        var replaceResult = UrlFetchApp.fetch(REPLACE_URL, replaceOptions);
        if (replaceResult.getResponseCode() == 200) {
            Logger.log('Key replacement successful for %s', user_email);
            MailApp.sendEmail({
                to: user_email,
                subject: "Delphi Epidata API Registration",
                noReply: true,
                body: `Thank you for registering with the Delphi Epidata API.

Your API key is: ${new_api_key}

Note: this email address was already registered, so a new key has been issued and your previous key has been deactivated.

For usage information, see the API Keys section of the documentation: https://cmu-delphi.github.io/delphi-epidata/api/api_keys.html

We strongly suggest you subscribe to our API mailing list to make sure you are informed on important topics, like announcements of API changes, details of updates to data, and unexpected downtime or other problems: https://lists.andrew.cmu.edu/mailman/listinfo/delphi-covidcast-api

Best,
Delphi Team`
            });
        } else {
            Logger.log('Key replacement failed for %s: %s %s', user_email, replaceResult.getResponseCode(), replaceResult.getContentText("UTF-8"));
        }
    }
};

function backfillRegistrationsSince(cutoffDate, dryRun) {
    dryRun = dryRun || false;
    if (dryRun) Logger.log('DRY RUN — no API calls or emails will be sent');

    var form = FormApp.getActiveForm();
    var allResponses = form.getResponses(cutoffDate);

    var results = { registered: [], alreadyHadKey: [], failed: [] };

    for (var ii = 0; ii < allResponses.length; ii++) {
        var user_email = allResponses[ii].getRespondentEmail();

        if (!user_email) {
            Logger.log('Skipping empty email at index %s', ii);
            continue;
        }

        var user_api_key = Math.random().toString(16).substr(2, 18);

        if (dryRun) {
            Logger.log('DRY RUN — would register: %s with key: %s', user_email, user_api_key);
            results.registered.push(user_email);
            continue;
        }

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

        var result = UrlFetchApp.fetch(POST_URL, options);
        var code = result.getResponseCode();

        if (code == 200) {
            Logger.log('Registered %s', user_email);
            results.registered.push(user_email);
            MailApp.sendEmail({
                to: user_email,
                subject: "Delphi Epidata API Registration",
                noReply: true,
                body: `Dear Delphi User,

Thank you for registering with the Delphi Epidata API.

Your API key is: ${user_api_key}

Because of an error on our part, there was a lengthy delay in this process, for which we apologize. We have now fixed the error.

For usage information, see the API Keys section of the documentation: https://cmu-delphi.github.io/delphi-epidata/api/api_keys.html

We strongly suggest you subscribe to our API mailing list to make sure you are informed on important topics, like announcements of API changes, details of updates to data, and unexpected downtime or other problems:

Adam Johns
Software Engineering Manager
Delphi Group
jajohns@andrew.cmu.edu`
            });
        } else if (code == 409) {
            Logger.log('Already registered, skipping: %s', user_email);
            results.alreadyHadKey.push(user_email);
        } else {
            Logger.log('Unexpected response %s for %s: %s', code, user_email, result.getContentText("UTF-8"));
            results.failed.push(user_email);
        }
    }

    Logger.log('Backfill complete. Registered: %s, Already had key: %s, Failed: %s',
        results.registered.length, results.alreadyHadKey.length, results.failed.length);
    Logger.log('Already had key: %s', JSON.stringify(results.alreadyHadKey));
    Logger.log('Failed: %s', JSON.stringify(results.failed));
}

function dryRunBackfillApril2026() {
    backfillRegistrationsSince(new Date('2026-04-17T00:00:00'), true);
}

function canaryTest() {
    backfillRegistrationsSince(new Date('2026-07-01T00:00:00'), false);
}

function runBackfillApril2026() {
    backfillRegistrationsSince(new Date('2026-04-17T00:00:00'));
}
