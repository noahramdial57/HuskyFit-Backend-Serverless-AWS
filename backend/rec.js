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
    let endpoint_name = 'pytorch-inference-2023-04-07-18-21-44-661'

     let params = {
                TableName: Table,
                Key: {
                    "UserID": UserId
                }
            }
    
     try {
        let data = await getItem(params)
        body = data.Item
        let weight = "100"
        let height = "5'0"
        
         try {
            weight = body.Weight
        } catch (err){
            // if attribute is empty
        }
        
         try {
            height = body.Height
        } catch (err){
            // if attribute is empty
        }

        try {
            Allergens = body.Allergens
        } catch (err){
            // if attribute is empty
        }
        
        try {
            diet_restr = body.Dietary_Restrictions
        } catch (err){
            // if attribute is empty
        }
        
        try {
            let tmp = body.Dining_Hall_Preference
            for (var i = 0; i < tmp.length; i++) {
                
                if (tmp[i] == "McMahon") {
                    dHallPref.push(tmp[i])

                } else{
                    dHallPref.push(tmp[i].toLowerCase())
                }
                
            }
            
        } catch (err){
            // if attribute is empty
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

        const responseBodyBreakfast = JSON.parse(breakfast.Body.toString());
        const responseBodyLunch = JSON.parse(lunch.Body.toString());
        const responseBodyDinner = JSON.parse(dinner.Body.toString());
        
        var recommendations = responseBodyBreakfast.concat(responseBodyLunch, responseBodyDinner);

        return {
            "isBase64Encoded": false,
            "headers": {
                "Content-Type": "application/json"
            },
            "statusCode": 200,
            "body": JSON.stringify(recommendations)
    };
    
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
