exports.handler = async (event) => {
    
    let profileInfo = {
        "name": event.requestContext.authorizer.claims.name,
        "birthdate": event.requestContext.authorizer.claims.birthdate,
        "email": event.requestContext.authorizer.claims.email
    }

    let statusCode = 200;
    const headers = {
    	"Content-Type": "application/json"
    };
          
    return {
        statusCode,
        headers,
        profileInfo
    }
  

}

