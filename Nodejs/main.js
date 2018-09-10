#!/usr/bin/env node

let port = parseInt(process.argv[2]);
const WebSocket = require('ws');
let amqp = require('amqplib/callback_api'); // message consumer
let request = require('request-promise'); // web service 
let sockets = new Map();
let amqp_conn;
const wss = new WebSocket.Server({ port: port });
const CONFIRM_URL = 'http://localhost:8000/user/session/token/confirm/json';
const AUTHENTICATION_URL = 'http://localhost:8000/user/session/token/auth/json';

console.log('socket port ' + port);

let ws_actions = {
    auth_msg: (data, web_socket) => {
        let token = data.token;
        let user_id = data.user_id;
        // llamamos web service authentication      
        request_authentication_user_socket(user_id, token, web_socket);
    },
    confirm_new_session: (data, web_socket) => {
        request_confirm_new_data(data.user_id,
            data.token, data.token_origin, web_socket, data.confirm);
    },
    create_instance: (data, web_socket) => {
        let success = 'create_instance';
        generate_amqp_channels(success, data.token, data.user_id);
        sockets.set(data.token, { user_id: data.user_id, web_socket: web_socket });
    }
};
let amqp_actions = {
    question_the_user: (data, token) => {
        let message = { 'type': 'confirm_new_session_token', 'data': { token: data.token } };
        message = JSON.stringify(message);
        console.log('Notificando a user con token :' + token);
        let socket = sockets.get(token).web_socket;
        if (socket.readyState === socket.OPEN) {
            socket.send(message);
        }
    },
    session_confirm: (data, token) => {
        let message = { 'type': 'close_message_confirm', 'data': { 'success': true } };
        message = JSON.stringify(message);
        let socket = sockets.get(token).web_socket;
        if (socket.readyState === socket.OPEN) {
            socket.send(message);
        }
    },
    success_session_redirect: (data, token, user_id) => {
        let message = {
            'type': 'success_session_redirect',
            'data': { 'success': data.success }
        };

        let success = (data.success ? 'authorized' : 'none');
        generate_amqp_channels(success, token, user_id);

        message = JSON.stringify(message);
        let socket = sockets.get(token).web_socket;
        if (socket.readyState === socket.OPEN) {
            socket.send(message);
        }
        if (data.success == false) {
            console.log('socket cerrado: ' + data.success + token);
            socket.close();
        }
    },
    create_instance_events: (data, token, user_id) => {
        let message = { 'type': 'create_instance_events', 'data': { 'message': data.message } };
        message = JSON.stringify(message);
        let data_user = sockets.get(token);
        let socket = data_user.web_socket;
        if (socket.readyState === socket.OPEN) {
            socket.send(message);
        }
        if (data.message == "done") {
            data_user.ch.unbindQueue(data_user.queue, 'topic_logs',
                'create_instance_events.' + token);
        }

    }
};

amqp.connect('amqp://localhost', function(err, conn) {
    amqp_conn = conn;
});


wss.on('connection', function connection(web_socket) {

    web_socket.on('message', function incoming(message) {
        let data_json = JSON.parse(message);
        ws_actions[data_json.type](data_json.data, web_socket);
    });
    web_socket.on('error', function error(err) {
        console.log('server socket error: ');
        console.log(err.stack);
    });
});

// cuando hay una nueva sesion se conecta al web services de django
// para verificar si el token de sesion es correcto
async function request_authentication_user_socket(user_id, token, web_socket) {
    let options = {
        uri: AUTHENTICATION_URL,
        qs: {
            token: token
        },
        headers: {
            'User-Agent': 'Request-Promise'
        },
        json: true
    };
    try {
        let repos = await request(options);

        let valid = repos.valid;
        if (!valid) {
            web_socket.close();
            console.log('WebSocket close');
            return;
        }
        sockets.set(token, { user_id: user_id, web_socket: web_socket });
        if (sockets.get(token) == null) {
            let success = (repos.first ? 'authorized' : 'waiting');
            generate_amqp_channels(success, token, user_id);
        }
        // cada vez que cambie de pagina se autentifica lo que hace que se desactive
        // el web socket y entonces se guarda

        console.log(new Date() + 'coneccion correcta');
    } catch (err) {
        console.log(err);
    }
};

// conecion con web service la repuesta del usuario YES o NO
// permite o no una nueva sesion
function request_confirm_new_data(user_id, token, token_origin,
    web_socket, confirm) {

    let options = {
        uri: CONFIRM_URL,
        qs: {
            token: token,
            token_origin: token_origin,
            confirm: confirm
        },
        headers: {
            'User-Agent': 'Request-Promise'
        },
        json: true
    };
    request(options).catch(function(err) {
        console.log(err);
    });

};


async function generate_amqp_channels(type_accions, token, user_id) {
    let amqp_group = {
        'authorized': ['question_the_user.' + user_id, 'session_confirm.' + user_id],
        'waiting': ['success_session_redirect.' + token],
        'none': null,
        'create_instance': ['create_instance_events.' + token]
    };
    let amqp_channels = amqp_group[type_accions];
    let data_user = (sockets.get(token) ? sockets.get(token) : {});

    if (amqp_channels != null) {
        console.log('>> es un usuario con privilegion :' + type_accions + ' token: ' + token);
        let ch = await create_amqp_channel();
        let ex = 'topic_logs';
        ch.assertExchange(ex, 'topic', { durable: false });
        let new_q = await assert_queue(ch, '', { exclusive: true });
        console.log('[*] esperado mensajes de django');

        amqp_channels.forEach(function(key) {
            ch.bindQueue(new_q.queue, ex, key);
        });
        data_user.ch = ch;
        data_user.queue = new_q.queue;
        data_user.amqp_channels = amqp_channels;
        sockets.set(token, data_user);

        ch.consume(new_q.queue, generate_amqp_message_consumer(token, user_id), { noAck: true });
    }


}




function generate_amqp_message_consumer(token, user_id) {
    return function(msg) {
        let data = JSON.parse(msg.content.toString());
        let msg_routing = msg.fields.routingKey;
        let indexOf = msg_routing.indexOf('.');
        let key = msg_routing.substr(0, indexOf);
        amqp_actions[key](data, token, user_id);
        console.log(new Date() + ' [django dice] %s:%s',
            msg.fields.routingKey,
            msg.content.toString());
    }
}

function delete_queue(ch, q_name, q_options) {
    return new Promise(function(resolve, reject) {
        ch.deleteQueue(q_name, q_options, function(err, ok) {
            if (err) {
                reject(err);
            } else {
                resolve(ok);
            }
        });
    });
}


function create_amqp_channel() {
    return new Promise(function(resolve, reject) {
        amqp_conn.createChannel(function(err, ch) {
            if (err) {
                reject(err);
            } else {
                resolve(ch);
            }
        });
    });
}


function assert_queue(ch, q_name, q_options) {
    return new Promise(function(resolve, reject) {
        ch.assertQueue(q_name, q_options, function(err, q) {
            if (err) {
                reject(err);
            } else {
                resolve(q);
            }
        });
    });
}