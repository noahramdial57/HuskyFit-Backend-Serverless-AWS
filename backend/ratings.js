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
    let rating = [parse] // workout 
    let method = JSON.parse(JSON.stringify(event.httpMethod))

    switch (method) {

        // Add new rating
        case "PUT":
            let params1 = {
                TableName: Table,
                ExpressionAttributeNames: {
                    "#Y": "Ratings"
                },
                ExpressionAttributeValues: {
                    ":y": rating
                },
                Key: {
                    UserID: UserId,
                },
                ConditionExpression: "attribute_exists(Ratings)",
                UpdateExpression: "SET #Y = list_append(#Y,:y)"
            };

            try {
                // Rating has been added to existing dataset
                const data = await dynamo.update(params1).promise();
                body = JSON.stringify("Rating has been recorded")

                return {
                    "isBase64Encoded": false,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "statusCode": 200,
                    "body": body
                };

            } catch (err) {
                // Rating dataset must be created
                await dynamo
                    .put({
                        TableName: Table,
                        Item: {
                            "UserID": UserId,
                            "Ratings": rating
                        }
                    })
                    .promise();
                body = JSON.stringify("Rating has been recorded")
                
                return {
                    "isBase64Encoded": false,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "statusCode": 200,
                    "body": body
                };
            }
            
        case "GET":
            let params = {
                TableName: Table,
                Key: {
                    "UserID": UserId,
                }
            }

            try {
                let data = await getItem(params)
                body = JSON.stringify(data.Item.Ratings)
            } catch (err) {
                console.log(err)
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
        "body": JSON.stringify("Error has occured. Rating not added")
    };
};