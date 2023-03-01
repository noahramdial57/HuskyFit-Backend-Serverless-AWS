exports.handler = async (event) => {
    
    let name  = event.requestContext.authorizer.claims.name
    let dob   = event.requestContext.authorizer.claims.birthdate
    let email = event.requestContext.authorizer.claims.email
    
    let body = {
        "Name": name,
        "Dob": dob,
        "Email": email
    }
          
    return {
        "isBase64Encoded": false,
        "headers": {
            "Content-Type": "application/json"
        },
        "statusCode": 200,
        "body": JSON.stringify(body)
    };
  

}

