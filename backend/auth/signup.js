const AWS = require('aws-sdk')
const {
    sendResponse,
    validateInput,
    validateInputSignup
} = require("./validate");

const cognito = new AWS.CognitoIdentityServiceProvider()

module.exports.handler = async (event) => {
    try {
        const isValid = validateInputSignup(event.body)
        if (!isValid)
            return sendResponse(400, {
                message: 'Invalid input'
            })

        // include new attributes
        const { name, email, password, birthdate} = JSON.parse(event.body)
        const { user_pool_id } = process.env
        const params = {
            UserPoolId: user_pool_id,
            Username: email,
            UserAttributes: [{
                    Name: 'email',
                    Value: email
                },
                {
                    Name: 'email_verified',
                    Value: 'true'
                },
                {
                    Name: 'name',
                    Value: name
                },
                {
                    Name: "birthdate",
                    Value: birthdate
                }
            ],
            MessageAction: 'SUPPRESS'
        }
        const response = await cognito.adminCreateUser(params).promise();
        if (response.User) {
            const paramsForSetPass = {
                Password: password,
                UserPoolId: user_pool_id,
                Username: email,
                Permanent: true
            };
            await cognito.adminSetUserPassword(paramsForSetPass).promise()
        }
        console.log(name + " has successfully signed up for HuskyFit.")
        return sendResponse(200, {
            message: 'User registration successful'
        })
    } catch (error) {
        const message = error.message ? error.message : 'Internal server error'
        return sendResponse(500, {
            message
        })
    }
}