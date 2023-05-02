const AWS = require('aws-sdk')
const { sendResponse, validateInputLogin } = require("./validate");

const cognito = new AWS.CognitoIdentityServiceProvider()

module.exports.handler = async (event) => {

    if (event.source === 'serverless-plugin-warmup') {
        console.log('WarmUp - Lambda is warm!');
        return 'Lambda is warm!';
      }
      
    try {
        const isValid = validateInputLogin(event.body)
        if (!isValid)
            return sendResponse(400, { message: 'Invalid input' })

        const { email, password } = JSON.parse(event.body)
        const { user_pool_id, client_id } = process.env
        const params = {
            AuthFlow: "ADMIN_NO_SRP_AUTH",
            UserPoolId: user_pool_id,
            ClientId: client_id,
            AuthParameters: {
                USERNAME: email,
                PASSWORD: password
            }
        }
        const response = await cognito.adminInitiateAuth(params).promise();
        console.log(email + " has successfully logged into HuskyFit.")
        return sendResponse(200, { message: 'Success', token: response.AuthenticationResult.IdToken })
    }
    catch (error) {
        const message = error.message ? error.message : 'Internal server error'
        return sendResponse(500, { message })
    }
}
