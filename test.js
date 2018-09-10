let amqp = require('amqplib/callback_api');

amqp.connect('amqp://localhost', async function(err, conn) {
    let ch = await create_amqp_channel(conn);
    console.log(ch);
});

function create_amqp_channel(conn) {
    return new Promise(function (resolve, reject) {
        conn.createChannel(function(err, ch) {
            if (err) {
                reject(err);
            }
            else {
                resolve(ch);
            }
        });
    });
}
