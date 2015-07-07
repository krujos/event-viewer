Oooh I'm Telling
================

`cf events` is pretty handy, but is parhaps a little hard to visualize.

Firstly, we need a client with cloud_controller.admin authority, otherwise you won't be able to see anything.
#Add a client
```
uaac client add event-viewer --scope uaa.none --authorized_grant_types "authorization_code, client_credentials, refresh_token"  --authorities "scim.read clients.read uaa.admin cloud_controller.admin cloud_controller.read scim.me clients.read"
```

#Present UAA & CloudController to the APP

In an untested theory you can give your client_id a grant other than client_credentials, but I've only tested this and the code assumes that the UAA URI will return 
json which contains an `access_token` that it will then insert as a `bearer` token in future requests to the CF CLI. It also assumes uaa provides an `expires_in` field that it will use to grab a new token.

`cf cups uaa -p '{ "uri": "https://uaa.10.244.0.34.xip.io/oauth/token?grant_type=client_credentials", "client_id": "oohimtelling", "client_secret": "oohimtelling" }'`

`cf cups cloud_controller -p '{ "uri": "https://api.10.244.0.34.xip.io" }'`

#Auth
The app uses http basic auth. Reuse the client_id and client_secret when challenged for creds. 

#Test it locally
source `env.sh` into your environment to get `VCAP_SERVICES` set locally. It assumes you're using bosh-lite and have created the client as I have above. 

```
$ python app.py
```
Browse to `localhost:8003/apps`

Should yield you some json that looks something like this

```
{
  "apps": [
    [
      {
        "buildpack": "Node.js",
        "created_at": "2015-05-23T23:04:00Z",
        "name": "node_v1.0",
        "org": "test-org",
        "routes": [
          "node.10.244.0.34.xip.io",
          "node-prod.10.244.0.34.xip.io"
        ],
        "space": "test-space",
        "updated_at": "2015-05-29T05:43:14Z"
      }
    ],
    [
      {
        "buildpack": "Node.js",
        "created_at": "2015-05-24T00:34:20Z",
        "name": "node_v1.1",
        "org": "test-org",
        "routes": [
          "node2.10.244.0.34.xip.io",
          "node-prod.10.244.0.34.xip.io"
        ],
        "space": "test-space",
        "updated_at": "2015-05-29T05:43:14Z"
      }
    ],
    [
      {
        "buildpack": "PHP",
        "created_at": "2015-06-04T04:16:59Z",
        "name": "php",
        "org": "jdk-org",
        "routes": [
          "php-odontophorous-shovelhead.10.244.0.34.xip.io"
        ],
        "space": "jdk-space",
        "updated_at": "2015-06-04T04:17:19Z"
      }
    ]
  ]
}

```

#Push it to CF
Make sure you didn't skip the `cups` step above, that would be a disaster. 

`cf push`

Browse to <cf-url>/apps

#TODO
* Maybe an html page at the route
* Make skipping ssl validation an option
* Basic auth with the client secret maybe... 