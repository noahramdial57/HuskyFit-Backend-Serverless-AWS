const AWS = require("aws-sdk");
const dynamo = new AWS.DynamoDB.DocumentClient();
const sagemakerRuntime = new AWS.SageMakerRuntime();

async function getItem(params) {
    try {
        const data = await dynamo.get(params).promise()
        return data
    } catch (err) {
        return err
    }
}

exports.handler = async (event) => {

    if (event.source === 'serverless-plugin-warmup') {
        console.log('WarmUp - Lambda is warm!');
        return 'Lambda is warm!';
      }
    
    let body = "Nothing";
    let Table = "HuskyFit-User-Info" // process.env.Workout-Table
    let UserId = event.requestContext.authorizer.claims.sub
    let mock_id = "1000"
    
    let Allergens = []
    let diet_restr = []
    let dHallPref = []
    let endpoint_name = 'pytorch-inference-2023-03-29-02-01-00-581'

     let params = {
                TableName: Table,
                Key: {
                    "UserID": UserId
                }
            }
    
     try {
        let data = await getItem(params)
        body = JSON.stringify(data.Item)
        let weight = "100"
        let height = "5'0"
        
         try {
            weight = body.Item.Weight
        } catch (err){
            // if attribute is empty
        }
        
         try {
            height = body.Item.Height
        } catch (err){
            // if attribute is empty
        }

        try {
            Allergens = body.Item.Allergens
        } catch (err){
            // if attribute is empty
        }
        
        try {
            diet_restr = body.item.Dietary_Restrictions
        } catch (err){
            // if attribute is empty
            // console.log(err)
        }
        
        try {
            dHallPref = body.item.Dining_Hall_Preference
        } catch (err){
            // if attribute is empty
            // console.log(err)
        }

        const payload_breakfast = {
            inputs:{
                  "UserID": mock_id,
                  "Weight": weight,
                  "Height": height,
                  "Dining Hall Preference": dHallPref,
                  "Allergens": Allergens,
                  "Dietary Restrictions": diet_restr,
                  "Meal": "Breakfast"
            }
        };
        
        const params_breakfast = {
          Body: JSON.stringify(payload_breakfast), // this works for some reason
          EndpointName: endpoint_name,
          ContentType: 'application/json',
          Accept: 'application/json'
        };
        
        const payload_lunch = {
            inputs:{
                  "UserID": mock_id,
                  "Weight": weight,
                  "Height": height,
                  "Dining Hall Preference": dHallPref,
                  "Allergens": Allergens,
                  "Dietary Restrictions": diet_restr,
                  "Meal": "Lunch"
            }
        };
        
        const params_lunch = {
          Body: JSON.stringify(payload_lunch), // this works for some reason
          EndpointName: endpoint_name,
          ContentType: 'application/json',
          Accept: 'application/json'
        };
        
        const payload_dinner = {
            inputs:{
                  "UserID": mock_id,
                  "Weight": weight,
                  "Height": height,
                  "Dining Hall Preference": dHallPref,
                  "Allergens": Allergens,
                  "Dietary Restrictions": diet_restr,
                  "Meal": "Dinner"
            }
        };
        
        const params_dinner = {
          Body: JSON.stringify(payload_dinner), // this works for some reason
          EndpointName: endpoint_name,
          ContentType: 'application/json',
          Accept: 'application/json'
        };
        
        const breakfast = await sagemakerRuntime.invokeEndpoint(params_breakfast).promise();
        const lunch = await sagemakerRuntime.invokeEndpoint(params_lunch).promise();
        const dinner = await sagemakerRuntime.invokeEndpoint(params_dinner).promise();

        const responseBodyBreakfast = breakfast.Body.toString();
        const responseBodyLunch = lunch.Body.toString();
        const responseBodyDinner = dinner.Body.toString();
        
        var recommendations = responseBodyBreakfast.concat(responseBodyLunch, responseBodyDinner);

        return {
            "isBase64Encoded": false,
            "headers": {
                "Content-Type": "application/json"
            },
            "statusCode": 200,
            "body": recommendations
    };

        // Process the response from the endpoint
        // console.log(responseBody);

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
};
