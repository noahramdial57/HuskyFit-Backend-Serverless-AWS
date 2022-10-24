# UConnFit-Backend-AWS

## Install AWS CLI
To download AWS CLI check out this [link.](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

To Configure AWS on your local machine run the following command:

```
aws configure
```

Your terminal should look like this:

![Look Here](https://miro.medium.com/max/1400/1*56pF8cszs0sK2KP_6hyW4Q.png)

## Install Serverless
Once you have the AWS CLI installed, we need to install serverless. Make sure you have Node version 16 downloaded

```
npm install -g serverless
```

Now clone down the repository.

```
git clone https://github.com/noahramdial57/UConnFit-Backend-AWS.git
```

```
cd backend
```

Run the following command to make sure all dependencies are installed.

```
npm install
```

## Test for functionality
Run the following command:

```
sls offline
```

Paste this URL in your web browser (or whatever URL you see in your terminal:
```
http://localhost:3000/dev/
```
