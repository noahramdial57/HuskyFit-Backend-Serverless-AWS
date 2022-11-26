const sendResponse = (statusCode, body) => {
    const response = {
        statusCode: statusCode,
        body: JSON.stringify(body),
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': true
        }
    }
    return response
}

const validateInputLogin = (data) => {
    const body = JSON.parse(data);
    const { email, password } = body
    if (!email || !password || password.length < 8)
        return false
    return true
}

const validateInputSignup = (data) => {
    const body = JSON.parse(data);
    const { name, email, password, birthdate } = body
    if (!name || !email || !password || !birthdate || password.length < 8)
        return false
    return true
}

module.exports = {
    sendResponse, validateInputLogin, validateInputSignup
};
