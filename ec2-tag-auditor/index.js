'use strict';
console.log('Loading function');

let AWS = require('aws-sdk');
let ec2 = new AWS.EC2({
    apiVersion: '2016-11-15'
});

exports.handler = (event, context, callback) => {
    console.log(event);

    let params = {
        DryRun: false,
        Filters: [{
            "Name": "instance-state-name",
            "Values": ["running"]
        }]
    };

    ec2.describeInstances(params, function (err, data) {
        if (err) {
            console.log("Error", err.stack);
        } else {
            
            var toTerminate = {
              InstanceIds: [],
              DryRun: false,
              Force: true
            };
            
            for(let inst of data["Reservations"][0]["Instances"]) {
                inst.Tags.forEach(function(tag) {
                    if(tag.Key != "Something") {
                        console.log("FAILED");
                        console.log(inst.InstanceId);
                        toTerminate.InstanceIds.push(inst.InstanceId);
                    } else {
                        console.log("SUCCESS");
                    }
                });
            }
            
            console.log(toTerminate);
            
            if(toTerminate.InstanceIds.length > 0) {
                ec2.stopInstances(toTerminate, function(err, data) {
                    if (err) console.log(err, err.stack); // an error occurred
                    else     console.log(data);           // successful response 
                });
            }
        }
    });
    
    callback(null, "Complete.");
};