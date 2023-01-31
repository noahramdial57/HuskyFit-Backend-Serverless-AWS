const { sendResponse } = require('./validate')

module.exports.handler = async (event) => {
    return sendResponse(200, { message: `${event.requestContext.authorizer.claims.name} has been successfully logged in!` })
}
