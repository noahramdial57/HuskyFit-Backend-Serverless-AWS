const AWS = require("aws-sdk");
const dynamo = new AWS.DynamoDB.DocumentClient();

async function getItem(params) {
    try {
        const data = await dynamo.get(params).promise()
        return data
    } catch (err) {
        return err
    }
}

exports.handler = async (event) => {

    let body = "Nothing";
    let Table = "HuskyFit-User-Info" 
    let parse = JSON.parse(event.body)

    let UserId = event.requestContext.authorizer.claims.sub
    let method = JSON.parse(JSON.stringify(event.httpMethod))

    switch (method) {

        // Add item to database
        case "PUT":
            await dynamo
                .put({
                    TableName: Table,
                    Item: {
                        "UserID": UserId,
                        "Weight": parse.Weight,
                        "Height": parse.Height,
                        "Allergens": parse.Allergens,
                        "Dietary Restrictions": parse.Dietary_restrictions

                    }
                })
                .promise();
            body = JSON.stringify("User info successfully added to database")

            return {
                "isBase64Encoded": false,
                "headers": {
                    "Content-Type": "application/json"
                },
                "statusCode": 200,
                "body": body
            };
        
        case "GET":
            let params = {
                TableName: Table,
                Key: {
                    "UserID": UserId,
                }
            }

            try {
                let data = await getItem(params)
                body = JSON.stringify(data.Item)
            } catch (err) {
                console.log(err)
                body = JSON.stringify("There was an error retrieving User Info.")
            }

            return {
                "isBase64Encoded": false,
                "headers": {
                    "Content-Type": "application/json"
                },
                "statusCode": 200,
                "body": body
            };
                

    }

    return {
        "isBase64Encoded": false,
        "headers": {
            "Content-Type": "application/json"
        },
        "statusCode": 404,
        "body": JSON.stringify("Error has occured.")
    };
}