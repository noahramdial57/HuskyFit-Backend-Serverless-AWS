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
    
    // Name of the workout table
    let Table = "HuskyFit-Food-Logs" // process.env.Workout-Table
    
    // Parse out the event body
    let parse = JSON.parse(event.body)
    
    // Get todays date to store workout
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0'); 
    var yyyy = today.getFullYear();
    let date = mm + '/' + dd + '/' + yyyy;

    let UserId = event.requestContext.authorizer.claims.sub
    let item = [parse] // food log 
    let method = JSON.parse(JSON.stringify(event.httpMethod))

    switch (method) {

        // Add new Workout | This Works!!
        case "PUT":

            let params1 = {
                TableName: Table,
                ExpressionAttributeNames: {
                    "#Y": "Food_Log"
                },
                ExpressionAttributeValues: {
                    ":y": item
                },
                Key: {
                    UserID: UserId,
                    Date: date
                },
                ConditionExpression: "attribute_exists(Food_Log)",
                UpdateExpression: "SET #Y = list_append(#Y,:y)"
            };

            try {
                // Workout has been added to existing dataset
                const data = await dynamo.update(params1).promise();
                body = JSON.stringify("Food log has been added")

                return {
                    "isBase64Encoded": false,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "statusCode": 200,
                    "body": body
                };

            } catch (err) {
                // Workout dataset must be created
                await dynamo
                    .put({
                        TableName: Table,
                        Item: {
                            "UserID": UserId,
                            "Date": date,
                            "Food_Log": item
                        }
                    })
                    .promise();
                body = JSON.stringify("Food log successfully added to database")
                
                return {
                    "isBase64Encoded": false,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "statusCode": 200,
                    "body": body
                };
            }

        // Get all of the users food logs for a specific date | This Works!!
        case "POST":
            date = parse.Date
            let params = {
                TableName: Table,
                Key: {
                    "UserID": UserId,
                    "Date": date
                }
            }

            try {
                let data = await getItem(params)
                body = JSON.stringify(data.Item)
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
        "body": JSON.stringify("Error has occured. Item not added")
    };
};